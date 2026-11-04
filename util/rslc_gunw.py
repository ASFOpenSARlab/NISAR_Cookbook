import copy
from datetime import datetime
import os
from pathlib import Path
from getpass import getpass
import re
import subprocess
import sys
import time

import sardem.dem

import h5py
import netrc as netrc_module
import numpy as np
import shapely
from ruamel.yaml import YAML

def get_rslc_summary(path):
    """

    """
    with h5py.File(path, "r") as f:
        root = f["science/LSAR"]
        ident = root["identification"]
        swaths = root["RSLC"]["swaths"]

        def get(key):
            if key not in ident:
                return None
            v = ident[key][()]
            if isinstance(v, bytes):
                return v.decode()
            if isinstance(v, np.ndarray):
                v = v.ravel()
                return v[0].decode() if v.size == 1 and isinstance(v[0], bytes) else v.tolist()
            return v.item() if hasattr(v, "item") else v

        freqs = {}
        for name in swaths:
            if name.startswith("frequency"):
                g = swaths[name]
                pols = [p.decode() for p in g["listOfPolarizations"][()]]
                freqs[name[-1]] = dict(
                    pols=pols,
                    bandwidth_mhz=round(float(g["processedRangeBandwidth"][()]) / 1e6, 2),
                    center_frequency=float(g["processedCenterFrequency"][()]),
                    shape=g[pols[0]].shape if pols and pols[0] in g else None)
        start = get("zeroDopplerStartTime")
        return dict(
            file=Path(path).name,
            cycle=get("granuleId").split("_")[4],
            mode=get("granuleId").split("_")[9],
            track=get("trackNumber"), frame=get("frameNumber"),
            pass_direction=str(get("orbitPassDirection")).lower(),
            look=str(get("lookDirection")).lower(),
            start=start,
            start_dt=datetime.fromisoformat(start[:26]),
            start_string=get("granuleId").split("_")[11],
            end_string=get("granuleId").split("_")[12],
            freqs=freqs, footprint=shapely.from_wkt(get("boundingPolygon")))
        
def ensure_earthdata_netrc():
    """
    Checks for the existance of a ~/.netrc with Earthdata Login credentials.
    Creates or updates ~/.netrc with EDL credentials if needed.
    """
    netrc_path = Path.home() / ".netrc"
    host = "urs.earthdata.nasa.gov"

    if netrc_path.exists():
        try:
            if netrc_module.netrc(netrc_path).authenticators(host):
                return
        except (netrc_module.NetrcParseError, OSError):
            raise ValueError(f"Cannot parse {netrc_path}")

    username = input("Earthdata Login username: ")
    password = getpass("Earthdata Login password: ")

    with netrc_path.open("a") as f:
        f.write(f"\nmachine {host}\n")
        f.write(f"    login {username}\n")
        f.write(f"    password {password}\n")

    os.chmod(netrc_path, 0o600)

def dem_bounds(footprints, margin_km=5.0):
    min_x, min_y, max_x, max_y = shapely.union_all(footprints).bounds
    lat = max(abs(min_y), abs(max_y))
    d_lat = margin_km / 111.0
    d_lon = margin_km / (111.0 * max(np.cos(np.deg2rad(lat)), 0.05))
    return (min_x - d_lon, max(min_y - d_lat, -90), max_x + d_lon, min(max_y + d_lat, 90))


def stage_dem(footprints, out_path):
    ensure_earthdata_netrc()
    tmp = Path(str(out_path) + ".part.tif") # store partially downloaded dem at temp .part.tif path
    sardem.dem.main(output_name=str(tmp), bbox=dem_bounds(footprints), data_source="NISAR",
                    output_format="GTiff", output_type="float32")
    tmp.replace(out_path) # Update to final path after download is complete
    return Path(out_path)


    paths = {
        "reference_rslc_file": ref_rslc_path,
        "secondary_rslc_file": sec_rslc_path,
        "work_path": work_path,
        "gunw_work_path": gunw_work_path,
        "dem_file": dem_path,
        "out_dir": out_dir,
        "scratch_dir": scratch_dir,
        "qa_dir": qa_dir,
        "log_path": log_path,
    }

def write_custom_gunw_config(gunw_config, ref, sec, paths, epsg, geocode_bounds, polarization, schema):
    rc = copy.deepcopy(gunw_config)
    groups = rc["runconfig"]["groups"]
    proc = groups["processing"]
    groups["input_file_group"] = {"reference_rslc_file": str(paths["reference_rslc_file"]), "secondary_rslc_file": str(paths["secondary_rslc_file"]),
                                  "qa_gunw_input_file": str(paths["gunw_work_path"])}


    dem_description = "NISAR DEM v1.2: Copernicus DEM GLO-30 (2023_1) referenced to the WGS84 ellipsoid, https://doi.org/10.5067/NIDEM-1"
    
    groups["dynamic_ancillary_file_group"] = {
        "dem_file": str(paths["dem_file"]), "dem_file_description": dem_description,
        "water_mask_file": None,
        "orbit_files": {"reference_orbit_file": None, "secondary_orbit_file": None},
        "troposphere_weather_model_files": {"reference_troposphere_file": None, "secondary_troposphere_file": None},
        "tec_file": None}
    groups["product_path_group"] = {"product_path": str(paths["out_dir"]), "scratch_path": str(paths["scratch_dir"]),
                                    "sas_output_file": str(paths["gunw_work_path"]), "product_counter": 1,
                                    "qa_output_dir": str(paths["qa_dir"])}
    groups["primary_executable"]["processing_type"] = "OD"
    groups["logging"] = {"path": str(paths["log_path"]), "write_mode": "w"}

    proc["input_subset"]["list_of_frequencies"] = {"A": [polarization]}
    center = shapely.union_all([ref["footprint"], sec["footprint"]]).centroid
    geo = proc["geocode"]
    geo["output_epsg"] = epsg
    if geocode_bounds:
        x0, y0, x1, y1 = geocode_bounds
        
        geo["top_left"], geo["bottom_right"] = {"x_abs": x0, "y_abs": y1}, {"x_abs": x1, "y_abs": y0}
    else:
        geo["top_left"], geo["bottom_right"] = {"x_abs": None, "y_abs": None}, {"x_abs": None, "y_abs": None}
    proc["radar_grid_cubes"] = {"output_epsg": epsg, "output_posting": {"x_posting": None, "y_posting": None},
                                "top_left": {"x_abs": None, "y_abs": None},
                                "bottom_right": {"x_abs": None, "y_abs": None}}

    has_side_band = all(polarization in s["freqs"].get("B", {}).get("pols", []) for s in (ref, sec))
    if not has_side_band:
        proc["ionosphere_phase_correction"]["enabled"] = False
        print("  ionosphere OFF: no frequency B", polarization, "in both RSLCs")
    proc["troposphere_delay"]["enabled"] = False

    runconfig = paths["work_path"] / "runconfig_gunw.yaml"
    with open(runconfig, "w") as fh:
        yaml = YAML()
        yaml.default_flow_style = False
        yaml.dump(rc, fh)
    return runconfig


def run_insar(runconfig, work_dir, log_path, poll_s=5):
    cmd = [sys.executable, "-m", "nisar.workflows.insar", str(runconfig), "--restart"]
    stdout_path = work_dir / "insar_stdout.log"
    seen = len(log_path.read_text(errors="replace").splitlines()) if log_path.exists() else 0
    t0 = time.time()
    with open(stdout_path, "w") as out:
        p = subprocess.Popen(cmd, stdout=out, stderr=subprocess.STDOUT, cwd=work_dir, env=os.environ.copy())
        try:
            while True:
                done = p.poll() is not None
                if log_path.exists():
                    lines = log_path.read_text(errors="replace").splitlines()
                    for line in lines[seen:]:
                        if re.search(r"[Ss]uccessfully ran", line):
                            print(f"  [{(time.time() - t0) / 60:6.1f} min] {line.strip(' -')}")
                    seen = len(lines)
                if done:
                    break
                time.sleep(poll_s)
        except KeyboardInterrupt:
            p.terminate()
            p.wait()
            raise
    if p.returncode != 0:
        tail = stdout_path.read_text(errors="replace").splitlines()[-40:]
        raise RuntimeError(f"ISCE3 failed (exit {p.returncode}); last lines of {stdout_path}:\n" + "\n".join(tail))