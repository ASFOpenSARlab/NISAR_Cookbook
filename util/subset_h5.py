from pathlib import Path
import h5py
import numpy as np
from pyproj import Transformer
from shapely import wkt
from shapely.ops import transform


# Subset a NISAR HDF5 file using a WKT 
def subset_h5(input_file, aoi):

    input_file = Path(input_file)

    # Store the subset folder inside the scene-wide folder
    output_dir = input_file.parent / "subset"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"{input_file.stem}_subset.h5"

    # Find NISAR coordinate systems
    with h5py.File(input_file, "r") as src:
        coord_paths = _get_coord_paths(src)

        grid_info = {}

        for coord_path in coord_paths:
            coords = src[coord_path]

            x = coords["xCoordinates"][:]
            y = coords["yCoordinates"][:]
            epsg = int(coords["projection"][()])

            # Convert WKT AOI lat/lon coordinates to the NISAR projection 
            transformer = Transformer.from_crs(
                "EPSG:4326",
                f"EPSG:{epsg}",
                always_xy=True,
            )

            geom = transform(
                transformer.transform,
                wkt.loads(aoi),
            )

            west, south, east, north = geom.bounds

            # Find the pixel rows and columns that exist within AOI
            x_idx = np.where((x >= west) & (x <= east))[0]
            y_idx = np.where((y >= south) & (y <= north))[0]

            if x_idx.size == 0 or y_idx.size == 0:
                continue

            grid_info[coord_path] = {
                "x_slice": slice(x_idx.min(), x_idx.max() + 1),
                "y_slice": slice(y_idx.min(), y_idx.max() + 1),
                "grid_shape": (len(y), len(x)),
            }

    if not grid_info:
        raise ValueError(
            "The AOI is not located within the selected NISAR scene."
        )

    if output_file.exists():
        output_file.unlink()

    # Copy the entire HDF5 structure while clipping spatial datasets
    with h5py.File(input_file, "r") as src, h5py.File(output_file, "w") as dst:
        _copy_subset(
            src,
            dst,
            grid_info,
        )

    return output_file


# Get the coordinate paths for NISAR GSLC grids
def _get_coord_paths(h5_file):

    coord_paths = []

    def find_coords(name, item):
        if (
            isinstance(item, h5py.Group)
            and "/grids/frequency" in f"/{name}"
            and "xCoordinates" in item
            and "yCoordinates" in item
            and "projection" in item
        ):
            coord_paths.append(f"/{name}")

    h5_file.visititems(find_coords)

    if not coord_paths:
        raise ValueError("No coordinate datasets were found")

    return coord_paths


# Copy the HDF5 structure and subset
def _copy_subset(
    src,
    dst,
    grid_info,
    path="",
):

    # Copy group attributes
    for name, value in src.attrs.items():
        dst.attrs[name] = value

    for name, item in src.items():
        item_path = f"{path}/{name}"

        if isinstance(item, h5py.Group):
            group = dst.create_group(name)

            _copy_subset(
                item,
                group,
                grid_info,
                item_path,
            )

        elif isinstance(item, h5py.Dataset):

            subsetted = False

            for coord_path, info in grid_info.items():

                x_slice = info["x_slice"]
                y_slice = info["y_slice"]
                grid_shape = info["grid_shape"]

                if item_path == f"{coord_path}/xCoordinates":
                    data = item[x_slice]
                    subsetted = True
                    break

                elif item_path == f"{coord_path}/yCoordinates":
                    data = item[y_slice]
                    subsetted = True
                    break

                elif (
                    item_path.startswith(coord_path)
                    and item.ndim >= 2
                    and item.shape[-2:] == grid_shape
                ):
                    leading = (slice(None),) * (item.ndim - 2)
                    data = item[leading + (y_slice, x_slice)]
                    subsetted = True
                    break

            if subsetted:
                new_item = dst.create_dataset(
                    name,
                    data=data,
                    dtype=item.dtype,
                )

                # Copy dataset attributes
                for attr, value in item.attrs.items():
                    new_item.attrs[attr] = value

            else:
                src.copy(item, dst, name=name)

        elif isinstance(item, h5py.Datatype):
            dst[name] = item.dtype