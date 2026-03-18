import re
from pathlib import Path
from os import PathLike

import h5py
import numpy as np
import xarray as xr
import dask.array as da
from dask import delayed
from collections.abc import Iterable
from typing import Union, Any
import rioxarray


MetadataValue = Union[str, int, float, list[Any], dict[str, Any]]

_date_regex = re.compile(r"_(\d{8}T\d{6})_")


def _get_gcov_ts(filename: str) -> np.datetime64:
    """
    Parses an acquisition datetime from a NISAR L2 GCOV product filename.

    filename: A string filename of a GCOV product
    returns: An np.datetime64 object of the product's acquisition date
    """
    match = _date_regex.search(filename)
    if match:
        ts_str = match.group(1)
        # YYYYMMDDTHHMMSS -> YYYY-MM-DDTHH:MM:SS
        return np.datetime64(
            f"{ts_str[:4]}-{ts_str[4:6]}-{ts_str[6:8]}T"
            f"{ts_str[9:11]}:{ts_str[11:13]}:{ts_str[13:15]}"
        )
    return np.datetime64("NaT")


def _decode_metadata(value: np.generic | np.ndarray | bytes) -> MetadataValue:
    """
    Converts identification metadata retreived from an HDF5 GCOV dataset 
    into Python-native data types.

    value: A metadata value
    returns: The metadata converted into a Python-native data type 
    """
    if isinstance(value, (bytes, np.bytes_)):
        return value.decode("utf-8")
    if isinstance(value, np.ndarray):
        if value.dtype.kind == "S":  # bytes -> str
            return [x.decode("utf-8") for x in value]
        return value.tolist()
    if isinstance(value, np.generic):  # numpy scalar
        return value.item()
    return value


def _get_identification_metadata_dict(path: str | PathLike[str]) -> dict[str, MetadataValue]:
    """
    Creates a metadata dictionary from the `/science/LSAR/identification`
    group of a NISAR L2 GCOV HDF5 dataset.

    path: Path to the GCOV HDF5 dataset
    returns: A dictionary of string metadata keys and Python-native values
    """
    with h5py.File(path, "r") as f:
        group = f["/science/LSAR/identification"]
        out = {}
        for key, obj in group.items():
            if isinstance(obj, h5py.Dataset):
                out[key] = _decode_metadata(obj[()])
        return out


def _delayed_read(
    path: str | PathLike[str], 
    dset_path: str, 
    y_idx_slice: slice | None = None, 
    x_idx_slice: slice | None = None
):
    """
    Returns a delayed read of an HDF5 dataset, optionally with index-based subsetting.

    path: The path to the HDF5 file
    dset_path: The internal path to the dataset being loaded
    y_idx_slice: (optional) y-coordinate index slice
    x_idx_slice: (optional) x-coordinate index slice
    """
    @delayed
    def _read():
        with h5py.File(path, "r") as f:
            dset = f[dset_path]
            if y_idx_slice is not None or x_idx_slice is not None:
                return dset[y_idx_slice, x_idx_slice]
            return dset[...]
    return _read()


def _coord_slice_to_index_slice(coords: np.ndarray, coord_slice: slice) -> slice:
    """
    Converts a coord-based slice into an index-based slice.
    Handles both acsending and descending coordinate arrays.

    coords: A nd.array of coordinates
    coord_slice: A slice of coords contained within the coordinate array
    returns: An index-based slice cooresponding to coord_slice
    """
    if coord_slice is None:
        return slice(None)

    start_val = coord_slice.start
    stop_val = coord_slice.stop

    if start_val is None and stop_val is None:
        return slice(None)

    ascending = coords[0] < coords[-1]

    # Fill in missing ends with array bounds
    if start_val is None:
        start_val = coords[0] if ascending else coords[0]
    if stop_val is None:
        stop_val = coords[-1] if ascending else coords[-1]

    low = min(start_val, stop_val)
    high = max(start_val, stop_val)

    if ascending:
        mask = (coords >= low) & (coords <= high)
    else:
        mask = (coords <= high) & (coords >= low)

    idx = np.where(mask)[0]
    if idx.size == 0:
        raise ValueError(
            f"Coord range [{start_val}, {stop_val}] is not within dataset"
            f"[{coords.min()}, {coords.max()}]"
        )

    start_idx = int(idx[0])
    stop_idx = int(idx[-1]) + 1
    return slice(start_idx, stop_idx)


def load_gcov_ts_xr(
    gcov_paths: str | PathLike[str] | Iterable[str | PathLike[str]],
    vars_to_load: Iterable[str] = ["all"], 
    freqs: Iterable[str] = ["all"], # "A" and/or "B" may be valid options depending on the product
    y_slice=None, # same units as HDF5's yCoordinates
    x_slice=None,    # same units as HDF5's xCoordinates)
    chunks=(1, 1, 2048, 2048) # (time, freq, y, x)
):
    """
    Load individual NISAR L2 GCOV products or a time series as an xarray.Dataset.
    Optional spatial subsetting at read time. Select GCOV datasets to load by name
    and/or frequency.

    Defaults to loading full spatial coverage for all datasets in all available frequencies.
    Each time step's identification metadata is included as a variable along the time dimension.

    gcov_paths: Path/s to GCOV file/s
    vars_to_load: (Optional) Names of GCOV grid variables to load. Includes all available by default.
    freqs: (Optional) Frequencies to include (["A", "B"]). Includes all available by default.
    y_slice: (Optional) slice of y-coordinates for spatial subsetting (Use HDF5's yCoordinates units)
    x_slice: (Optional) slice of x-coordinates for spatial subsetting (Use HDF5's xCoordinates units)
    chunks: int
        Max chunk size along x/y dimensions.
    """
    # normalize path/s
    if not isinstance(gcov_paths, Iterable) or isinstance(gcov_paths, str):
        gcov_paths = [gcov_paths]
    gcov_paths = [Path(path) for path in gcov_paths]
    gcov_paths = sorted(gcov_paths)

    if "all" in vars_to_load:
        vars_to_load = [
            "HHHH", "VVVV", "HVHV", "VHVH",
            "HHHV", "HHVH", "HHVV",
            "HVVH", "HVVV", "VHVV",
            "mask", "numberOfLooks", "rtcGammaToSigmaFactor",
        ]

    # Read dataset-level metadata and type info from first image in time series
    with h5py.File(gcov_paths[0], "r") as f:
        if "all" in freqs:
            raw_freqs = f["/science/LSAR/identification/listOfFrequencies"][()]
            freqs = raw_freqs.astype(str).tolist()

        group = {freq: f"/science/LSAR/GCOV/grids/frequency{freq}" for freq in freqs}

        # x/y/projection from the first frequency that exists
        first_freq = freqs[0]
        g = f[group[first_freq]]

        x_full = g["xCoordinates"][...]
        y_full = g["yCoordinates"][...]
        proj = g["projection"][()]

        # convert coord-based slices to index-based slices
        if y_slice is not None:
            y_idx_slice = _coord_slice_to_index_slice(y_full, y_slice)
        else:
            y_idx_slice = slice(None)

        if x_slice is not None:
            x_idx_slice = _coord_slice_to_index_slice(x_full, x_slice)
        else:
            x_idx_slice = slice(None)

        # subset coord arrays for xr.Dataset
        y = y_full[y_idx_slice]
        x = x_full[x_idx_slice]
 
        ny, nx = len(y), len(x)

        # build dtype map for included datasets
        dtype_map = {}
        for v in vars_to_load:
            for freq in freqs:
                dset_path = f"{group[freq]}/{v}"
                if dset_path in f:
                    dtype_map[(freq, v)] = f[dset_path].dtype

    # time coordinate from filenames
    time = np.array([_get_gcov_ts(p.name) for p in gcov_paths])

    # Reduce oversized chunk sizes
    time_chunk = min(len(time), chunks[0])
    freq_chunk = min(len(freqs), chunks[1])
    y_chunk = min(ny, chunks[2])
    x_chunk = min(nx, chunks[3])
    chunks = (time_chunk, freq_chunk, y_chunk, x_chunk)

    data_vars = {}

    # stack the GCOV grid variables
    for v in vars_to_load:
        per_freq = []
        for freq in freqs:
            dt = dtype_map.get((freq, v))
            if dt is None:
                # this variable/freq combination not present in the first time step
                continue

            dset_path = f"/science/LSAR/GCOV/grids/frequency{freq}/{v}"

            time_slices = [
                da.from_delayed(
                    _delayed_read(p, dset_path, y_idx_slice=y_idx_slice, x_idx_slice=x_idx_slice),
                    shape=(ny, nx),
                    dtype=dt,
                )[None, None, ...]  # (time=1, freq=1, y, x)
                for p in gcov_paths
            ]

            per_freq.append(da.concatenate(time_slices, axis=0))  # stack over time

        if per_freq:
            stacked = da.concatenate(per_freq, axis=1).rechunk(chunks)
            data_vars[v] = (("time", "frequency", "y", "x"), stacked)

    # Add per time step identification metadata
    identification_stack = [_get_identification_metadata_dict(p) for p in gcov_paths]
    data_vars["identification"] = ("time", identification_stack)

    ds = xr.Dataset(
        data_vars=data_vars,
        coords={
            "time": time,
            "frequency": np.array(list(freqs)),
            "y": y,
            "x": x,
        },
        attrs={
            "source": "NISAR L2 GCOV"
        },
    )
    
    return ds.rio.write_crs(f"EPSG:{proj}")
