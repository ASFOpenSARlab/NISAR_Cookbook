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

    # Find NISAR coordinate system
    with h5py.File(input_file, "r") as src:
        coord_path = _get_coord_path(src)
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
        raise ValueError(
            "The AOI is not located within the selected NISAR scene."
        )

    x_slice = slice(x_idx.min(), x_idx.max() + 1)
    y_slice = slice(y_idx.min(), y_idx.max() + 1)

    if output_file.exists():
        output_file.unlink()

    # Copy the entire HDF5 structure while clipping spatial datasets
    with h5py.File(input_file, "r") as src, h5py.File(output_file, "w") as dst:
        _copy_subset(
            src,
            dst,
            coord_path,
            x_slice,
            y_slice,
            (len(y), len(x)),
        )

    return output_file

# Get the coordinate path for any geocoded NISAR HDF5 file 
def _get_coord_path(h5_file):

    coord_paths = []

    def find_coords(name, item):
        if (
            isinstance(item, h5py.Group)
            and "xCoordinates" in item
            and "yCoordinates" in item
            and "projection" in item
        ):
            coord_paths.append(f"/{name}")
            
    # Visititems() searches all groups for matching criteria (xCoordinates, yCoordinates, projection)
    h5_file.visititems(find_coords)

    if not coord_paths:
        raise ValueError("No coordinate datasets were found")

    return coord_paths[0]

# Copy the HDF5 structure and subset
def _copy_subset(
    src,
    dst,
    coord_path,
    x_slice,
    y_slice,
    grid_shape,
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
                coord_path,
                x_slice,
                y_slice,
                grid_shape,
                item_path,
            )

        elif isinstance(item, h5py.Dataset):

            if item_path == f"{coord_path}/xCoordinates":
                data = item[x_slice]

            elif item_path == f"{coord_path}/yCoordinates":
                data = item[y_slice]

            elif (
                item_path.startswith(coord_path)
                and item.ndim >= 2
                and item.shape[-2:] == grid_shape
            ):
                leading = (slice(None),) * (item.ndim - 2)
                data = item[leading + (y_slice, x_slice)]

            else:
                data = item[()]

            new_item = dst.create_dataset(
                name,
                data=data,
                dtype=item.dtype,
            )

            # Copy dataset attributes
            for attr, value in item.attrs.items():
                new_item.attrs[attr] = value

        elif isinstance(item, h5py.Datatype):
            dst[name] = item.dtype