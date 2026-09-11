"""
nisar_polsar.py
===============
SAR processing utilities for NISAR dual-pol GSLC analysis.

Functions
---------
refined_lee_filter              – Edge-preserving speckle filter (Lee, 1981)
compute_cloude_pottier          – H/alpha decomposition from [C2] eigenvalues
classify_cloude_pottier         – 9-zone H/alpha unsupervised classification
display_zone_breakdown          – Pixel-count table for H/alpha zones
export_zones_geotiff            – Save zone map as georeferenced GeoTIFF
compute_dpid                    – Dual-Pol Intensity Decomposition (DPID)
classify_dpid                   – 5-class scene-adaptive DPID classifier
display_dpid_breakdown          – Pixel-count table for DPID classes
export_dpid_geotiff             – Save 3-band DPID GeoTIFF
compute_rfbi                    – Radar Forest Biomass Index (RFBI)
export_rfbi_geotiff             – Save RFBI as single-band GeoTIFF

References
----------
Cloude & Pottier (1997) IEEE TGRS 35(1), 68-78.
Lee & Pottier (2009) Polarimetric Radar Imaging, CRC Press.
"""

import os
import numpy as np
import h5py
import hdf5plugin          # MUST be imported before h5py to enable NISAR decompression
import rasterio
from rasterio.transform import from_origin
from pyproj import CRS
from scipy.ndimage import uniform_filter

try:
    import cv2             # Used only in classify_cloude_pottier for medianBlur
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

try:
    import pandas as pd    # Used in display_*_breakdown; optional outside Jupyter
    _PANDAS_AVAILABLE = True
except ImportError:
    _PANDAS_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Speckle filter
# ─────────────────────────────────────────────────────────────────────────────

def refined_lee_filter(img, window_size=5):
    '''
    Edge-preserving speckle filter based on the Refined Lee algorithm (Lee, 1981).

    Each output pixel is a weighted blend of the local mean and the original
    pixel value:
        output = mean + k * (pixel - mean)
    where k = local_var / (local_var + noise_var) in [0, 1].

    In homogeneous areas k -> 0 (strong smoothing); near edges k -> 1 (no change).
    Local variance is computed efficiently via Var(X) = E[X^2] - E[X]^2 using
    two separable box-car (uniform) filters.

    Parameters
    ----------
    img : ndarray (2-D, float)
        Raw intensity image (linear scale, not dB).
    window_size : int
        Square averaging window size in pixels (default 5).

    Returns
    -------
    filtered : ndarray (2-D, float), same shape as img
    '''
    img_mean     = uniform_filter(img,    size=window_size)
    img_sqr_mean = uniform_filter(img**2, size=window_size)
    img_var      = np.maximum(img_sqr_mean - img_mean**2, 0)
    overall_var  = max(float(np.var(img)), 1e-6)
    k = np.clip(img_var / (img_var + overall_var / window_size**2), 0, 1)
    return img_mean + k * (img - img_mean)


# ─────────────────────────────────────────────────────────────────────────────
# Cloude-Pottier decomposition
# ─────────────────────────────────────────────────────────────────────────────

def compute_cloude_pottier(gslc_file_path, window_size=5, aoi_window=None):
    '''
    Cloude-Pottier H/alpha decomposition for NISAR dual-pol (HH/HV) GSLC data.

    Builds the 2x2 gamma-nought covariance matrix [C2] from the complex HH and
    HV SLC channels, speckle-filters each element with the Refined Lee filter,
    then solves the 2x2 eigenvalue problem analytically (quadratic formula) to
    obtain per-pixel Polarimetric Entropy H and Mean Scattering Angle alpha.

    Calibration
    -----------
    gamma0 = |S|^2 / scaleFactor^2  (NISAR GSLC product specification D-102272)
    scaleFactor is read per-polarisation from the HDF5 metadata.

    Parameters
    ----------
    gslc_file_path : str
        Absolute path to the NISAR GSLC HDF5 file.
    window_size : int
        Speckle filter window size (default 5 pixels).
    aoi_window : tuple or None
        (row_start, row_end, col_start, col_end).  Always specify an AOI --
        full NISAR scenes are ~30 000 x 30 000 pixels.

    Returns
    -------
    H : ndarray (2-D, float32)  -- Polarimetric entropy in [0, 1]
    mean_alpha_deg : ndarray (2-D, float32)  -- Mean scattering angle in [0, 90] deg
    '''
    abs_path  = os.path.abspath(gslc_file_path)
    base      = "/science/LSAR/GSLC/grids/frequencyA/"
    cal_path  = "/science/LSAR/GSLC/metadata/calibrationInformation/frequencyA/"

    with h5py.File(abs_path, 'r') as f:
        full_shape = f[f'{base}HH'].shape
        print(f"Full dataset: {full_shape[0]} rows x {full_shape[1]} cols")

        if aoi_window is not None:
            r0, r1, c0, c1 = aoi_window
            print(f"AOI: rows [{r0}:{r1}], cols [{c0}:{c1}]")
        else:
            r0, r1, c0, c1 = 0, full_shape[0], 0, full_shape[1]
            print("WARNING: No AOI -- full image loaded (may need > 10 GB RAM).")

        print("Reading HH and HV bands...")
        S_hh = f[f'{base}HH'][r0:r1, c0:c1]
        S_hv = f[f'{base}HV'][r0:r1, c0:c1]

        try:
            sf_hh = float(f[f'{cal_path}HH/scaleFactor'][()])
            sf_hv = float(f[f'{cal_path}HV/scaleFactor'][()])
        except KeyError:
            print("  Warning: scaleFactor not found -- proceeding uncalibrated (sf=1.0).")
            sf_hh = sf_hv = 1.0

    print(f"Scale factors  HH: {sf_hh:.4e}  HV: {sf_hv:.4e}")

    # Build gamma-nought covariance elements
    print("Building [C2] covariance matrix elements...")
    C11 = S_hh * np.conj(S_hh) / sf_hh**2
    C22 = S_hv * np.conj(S_hv) / sf_hv**2
    C12 = S_hh * np.conj(S_hv) / (sf_hh * sf_hv)

    # Speckle-filter each element (real and imaginary parts separately for C12)
    print("Applying Refined Lee filter to covariance elements...")
    C11_avg  = refined_lee_filter(np.real(C11), window_size)
    C22_avg  = refined_lee_filter(np.real(C22), window_size)
    C12_avg  = (refined_lee_filter(np.real(C12), window_size)
                + 1j * refined_lee_filter(np.imag(C12), window_size))

    # Eigenvalues of 2x2 Hermitian matrix via quadratic formula
    # lambda = (Tr +/- sqrt(Tr^2 - 4*Det)) / 2
    print("Computing eigenvalues...")
    trace        = C11_avg + C22_avg
    det          = C11_avg * C22_avg - np.abs(C12_avg)**2
    discriminant = np.sqrt(np.maximum(trace**2 - 4 * det, 0))
    L1 = (trace + discriminant) / 2.0
    L2 = (trace - discriminant) / 2.0

    span = L1 + L2
    span[span == 0] = 1e-6

    # Polarimetric entropy H = -sum(Pi * log2(Pi))
    print("Computing entropy H...")
    P1 = L1 / span
    P2 = L2 / span
    H = np.zeros_like(span, dtype=np.float32)
    for P in [P1, P2]:
        mask = P > 0
        H[mask] -= P[mask] * np.log2(P[mask])

    # Mean scattering angle alpha (weighted average of per-eigenvalue angles)
    print("Computing mean scattering angle alpha...")
    C12_abs = np.abs(C12_avg)
    C12_abs[C12_abs == 0] = 1e-6
    alpha1 = np.arctan2(np.abs(L1 - C11_avg), C12_abs)
    alpha2 = np.arctan2(np.abs(L2 - C11_avg), C12_abs)
    mean_alpha_deg = np.degrees(P1 * alpha1 + P2 * alpha2).astype(np.float32)

    return H, mean_alpha_deg

def classify_cloude_pottier(H, alpha_deg, apply_filter=True):
    '''
    Assign each pixel to one of nine H/alpha scattering zones using the
    dual-pol optimal dividing lines empirically derived for HH-HV SAR by
    Ji & Wu (2015, Table 2), rather than the classical full-polarimetric
    Cloude & Pottier (1997) thresholds (H = 0.5/0.9, alpha = 42.5/47.5),
    which are not valid outside the full-pol [T3] feasible region.

    Zone layout matches Ji & Wu (2015), Figure 1 (Z1 = lowest entropy/alpha,
    Z9 = highest entropy/alpha), NOT the earlier ad hoc numbering of this
    module:
        Low H  (< l1=0.66):        Z1 surface | Z2 dipole | Z3 multiple
        Medium H (l1-l2=0.66-0.93): Z4 surface | Z5 dipole | Z6 multiple
        High H (> l2=0.93):                    Z8 dipole | Z9 multiple

    Two caveats documented experimentally in Ji & Wu (2015) for HH-HV SAR:

    1. Z2 (low-entropy dipole) does not exist: the optimal boundary between
       Z1/Z2 (l3=33.5 deg) lies ABOVE the Z2/Z3 boundary (l4=31.3 deg), i.e.
       the two lines are inverted relative to the full-pol case, so there is
       no alpha band that resolves as "Z2 only". Pixels below the crossover
       (~32.4 deg) are assigned Z1, above it Z3, and Z2 is never populated.
    2. The high-entropy Z7/Z8 boundary is not resolvable for HH-HV SAR (Ji &
       Wu, 2015 give only l7=50.2 deg for the Z8/Z9 boundary; no dividing
       line for Z7/Z8 achieves an acceptable retention ratio). Z7 is
       therefore merged into Z8 here and left unpopulated, rather than
       drawn at an arbitrary, unvalidated angle.

    Even with these optimal lines, Ji & Wu (2015, Table 3) report that
    HH-HV SAR only retains ~29% of the scattering-mechanism labels that a
    fully polarimetric [T3] decomposition would assign (vs. ~68% for
    HH-VV) -- co-polarization is what actually separates surface, dipole,
    and dihedral scattering; HH-HV alone provides much weaker separation.
    See Section 1b of this notebook and `hhhv_canonical_scatterers()` for
    the underlying reason: the three canonical scattering mechanisms
    project onto the SAME point in the HH-HV H-alpha plane.

    Parameters
    ----------
    H : ndarray (2-D, float)         -- Entropy in [0, 1]
    alpha_deg : ndarray (2-D, float) -- Alpha angle in degrees [0, 90]
    apply_filter : bool              -- Apply 3x3 spatial median filter if True

    Returns
    -------
    zones : ndarray (2-D, uint8), labels 0 (background) to 9 (Z7 unused)
    '''
    print("Classifying pixels into 9 H/alpha zones (Ji & Wu 2015 HH-HV dividing lines)...")
    zones = np.zeros_like(H, dtype=np.uint8)

    # Table 2 (Ji & Wu, 2015), HH-VV/HH-HV/HV-VV row for HH-HV.
    l1, l2 = 0.66, 0.93                      # low/medium, medium/high entropy
    l3, l4 = 33.5, 31.3                      # Z1/Z2, Z2/Z3 (inverted -> Z2 empty)
    l5, l6 = 38.1, 48.4                      # Z4/Z5, Z5/Z6
    l7     = 50.2                            # Z8/Z9 (Z7/Z8 not resolvable -> Z7 merged into Z8)
    z1z3_crossover = (l3 + l4) / 2.0         # ~32.4 deg: single split replacing the degenerate Z2 band

    low_h  = H < l1
    med_h  = (H >= l1) & (H <= l2)
    high_h = H > l2

    zones[low_h  & (alpha_deg <  z1z3_crossover)] = 1   # Z1: low-H surface
    zones[low_h  & (alpha_deg >= z1z3_crossover)] = 3   # Z3: low-H multiple (Z2 does not exist)
    zones[med_h  & (alpha_deg <  l5)]             = 4   # Z4: medium-H surface
    zones[med_h  & (alpha_deg >= l5) & (alpha_deg < l6)] = 5  # Z5: medium-H dipole
    zones[med_h  & (alpha_deg >= l6)]             = 6   # Z6: medium-H multiple
    zones[high_h & (alpha_deg <  l7)]             = 8   # Z8: high-H dipole (Z7 merged in)
    zones[high_h & (alpha_deg >= l7)]             = 9   # Z9: high-H multiple
    zones[~np.isfinite(H) | ~np.isfinite(alpha_deg)] = 0

    if apply_filter and _CV2_AVAILABLE:
        print("Applying 3x3 spatial median filter...")
        zones = cv2.medianBlur(zones, ksize=3)
    elif apply_filter:
        print("  cv2 not available -- skipping median filter.")

    return zones


def display_zone_breakdown(zones_array):
    '''Print a Pandas table of pixel counts and coverage % for each H/alpha zone.'''
    zone_names = {
        0: "Background / NaN",
        1: "Z1 High-H Double-Bounce (flooded forest / dense urban)",
        2: "Z2 High-H Volume (dense forest canopy)",
        3: "Z3 High-H Surface (complex rough surfaces)",
        4: "Z4 Med-H Double-Bounce (urban / oriented structures)",
        5: "Z5 Med-H Volume (vegetation / crops)",
        6: "Z6 Med-H Surface (rough soil / moderate water)",
        7: "Z7 Low-H Double-Bounce (isolated buildings)",
        8: "Z8 Low-H Dipole (sparse vegetation / oriented crops)",
        9: "Z9 Low-H Surface (calm water / smooth bare ground)",
    }
    ids, counts = np.unique(zones_array, return_counts=True)
    counts_dict = dict(zip(ids, counts))
    total = sum(c for z, c in counts_dict.items() if z != 0)
    rows = [{"Zone": z, "Description": zone_names[z],
             "Pixels": f"{counts_dict.get(z,0):,}",
             "Coverage (%)": round(counts_dict.get(z,0) / total * 100 if total else 0, 2)}
            for z in range(1, 10)]
    if _PANDAS_AVAILABLE:
        df = __import__('pandas').DataFrame(rows).set_index("Zone")
        print(f"Total valid pixels: {total:,}")
        try:
            display(df)   # noqa: F821 -- Jupyter built-in
        except NameError:
            print(df.to_string())
    else:
        for r in rows:
            print(r)


def export_zones_geotiff(zones_array, gslc_file_path, output_tiff_path, aoi_window=None):
    '''
    Save the Cloude-Pottier zone classification as a georeferenced uint8 GeoTIFF.

    Geographic metadata (CRS, affine transform) is extracted from the source NISAR
    HDF5 file.  nodata=0 marks background / invalid pixels as transparent in GIS tools.

    Parameters
    ----------
    zones_array : ndarray (2-D, uint8)    -- Integer zone labels 0-9
    gslc_file_path : str                  -- Source HDF5 file (for geo metadata)
    output_tiff_path : str                -- Output .tif path
    aoi_window : tuple or None            -- (row_start, row_end, col_start, col_end)
    '''
    img_h, img_w = zones_array.shape
    transform, clean_crs = _read_geo_meta(gslc_file_path, img_h, img_w, aoi_window)
    profile = {'driver': 'GTiff', 'height': img_h, 'width': img_w, 'count': 1,
               'dtype': rasterio.uint8, 'crs': clean_crs, 'transform': transform,
               'nodata': 0, 'compress': 'lzw', 'tiled': True,
               'blockxsize': 256, 'blockysize': 256}
    print(f"Writing zone GeoTIFF to: {output_tiff_path}")
    with rasterio.open(output_tiff_path, 'w', **profile) as dst:
        dst.write(zones_array.astype(np.uint8), 1)
    print("Done.")


# ─────────────────────────────────────────────────────────────────────────────
# Dual-Pol Intensity Decomposition
# ─────────────────────────────────────────────────────────────────────────────

def compute_dpid(gslc_file_path, window_size=5, aoi_window=None):
    '''
    Compute the Dual-Pol Intensity Decomposition (DPID) from a NISAR GSLC file.

    Returns three speckle-filtered, gamma-nought calibrated channels:
      gamma0_hh  -- co-pol backscatter (sensitive to surfaces and double-bounce)
      gamma0_hv  -- cross-pol backscatter (sensitive to volume / vegetation)
      dcp        -- Degree of Cross-Polarization = gamma0_hv / gamma0_hh in [0, 1]

    These three channels form an RGB false-colour composite (R=HH, G=HV, B=DCP)
    that is physically valid for any linear dual-pol SAR configuration.

    Parameters
    ----------
    gslc_file_path : str    -- Path to the NISAR GSLC HDF5 file
    window_size : int       -- Speckle filter window size (default 5)
    aoi_window : tuple/None -- (row_start, row_end, col_start, col_end)

    Returns
    -------
    gamma0_hh, gamma0_hv, dcp : ndarray (2-D, float32)
    '''
    abs_path = os.path.abspath(gslc_file_path)
    grid     = "/science/LSAR/GSLC/grids/frequencyA/"
    cal      = "/science/LSAR/GSLC/metadata/calibrationInformation/frequencyA/"

    print("Reading HH and HV bands + calibration factors...")
    with h5py.File(abs_path, 'r') as f:
        full_shape = f[f'{grid}HH'].shape
        r0, r1, c0, c1 = aoi_window if aoi_window else (0, full_shape[0], 0, full_shape[1])
        S_hh = f[f'{grid}HH'][r0:r1, c0:c1]
        S_hv = f[f'{grid}HV'][r0:r1, c0:c1]
        try:
            sf_hh = float(f[f'{cal}HH/scaleFactor'][()])
            sf_hv = float(f[f'{cal}HV/scaleFactor'][()])
        except KeyError:
            print("  Warning: scaleFactor not found -- sf=1.0.")
            sf_hh = sf_hv = 1.0

    print(f"Scale factors  HH: {sf_hh:.4e}  HV: {sf_hv:.4e}")

    # Calibrated gamma-nought intensity: |S|^2 / scaleFactor^2
    I_hh = (np.real(S_hh * np.conj(S_hh)) / sf_hh**2).astype(np.float32)
    I_hv = (np.real(S_hv * np.conj(S_hv)) / sf_hv**2).astype(np.float32)

    # Speckle filtering in the intensity domain
    print("Applying Refined Lee filter...")
    gamma0_hh = refined_lee_filter(I_hh, window_size)
    gamma0_hv = refined_lee_filter(I_hv, window_size)

    # Degree of Cross-Polarization: fraction of power in cross-pol channel
    dcp = np.clip(gamma0_hv / (gamma0_hh + 1e-9), 0.0, 1.0)

    return gamma0_hh.astype(np.float32), gamma0_hv.astype(np.float32), dcp.astype(np.float32)


def classify_dpid(gamma0_hh, gamma0_hv, dcp):
    '''
    Five-class unsupervised classification from the DPID channels.

    Uses scene-adaptive percentile thresholds and a priority-override scheme:
      1 (lowest power) -- Calm Water
      2 (default)      -- Bare Soil / Open Land
      3                -- Dense Vegetation (high DCP, significant HV)
      4                -- Urban / Built-up (very high HH, low DCP)
      5                -- Wetlands (elevated both HH and HV)

    Parameters
    ----------
    gamma0_hh, gamma0_hv : ndarray (2-D, float) -- calibrated gamma-nought arrays
    dcp : ndarray (2-D, float)                   -- DCP ratio in [0, 1]

    Returns
    -------
    classes : ndarray (2-D, uint8), labels 0-5
    '''
    classes = np.zeros_like(gamma0_hh, dtype=np.uint8)
    finite  = np.isfinite(gamma0_hh) & np.isfinite(gamma0_hv) & np.isfinite(dcp)
    span    = gamma0_hh + gamma0_hv

    hh_f, hv_f, span_f = gamma0_hh[finite], gamma0_hv[finite], span[finite]
    p_span10 = np.percentile(span_f, 10)
    p_hh90   = np.percentile(hh_f,  90)
    p_hh60   = np.percentile(hh_f,  60)
    p_hv50   = np.percentile(hv_f,  50)
    p_hv60   = np.percentile(hv_f,  60)

    classes[finite] = 2  # default: bare soil
    classes[(dcp > 0.5) & (gamma0_hv > p_hv50) & finite] = 3
    classes[(gamma0_hh > p_hh60) & (gamma0_hv > p_hv60) & finite] = 5
    classes[(gamma0_hh > p_hh90) & (dcp < 0.4) & finite] = 4
    classes[(span < p_span10) & finite] = 1  # water: highest priority
    classes[~finite] = 0
    return classes


def display_dpid_breakdown(classes):
    '''Print a Pandas table of pixel counts and coverage % for each DPID class.'''
    names = {0: "Background", 1: "Calm Water", 2: "Bare Soil / Open Land",
             3: "Dense Vegetation", 4: "Urban / Built-up", 5: "Wetlands"}
    ids, counts = np.unique(classes, return_counts=True)
    cd = dict(zip(ids, counts))
    total = sum(c for i, c in cd.items() if i != 0)
    rows = [{"Class": i, "Description": names[i],
             "Pixels": f"{cd.get(i,0):,}",
             "Coverage (%)": round(cd.get(i,0) / total * 100 if total else 0, 2)}
            for i in range(1, 6)]
    if _PANDAS_AVAILABLE:
        df = __import__('pandas').DataFrame(rows).set_index("Class")
        print(f"Total valid pixels: {total:,}")
        try:
            display(df)   # noqa: F821
        except NameError:
            print(df.to_string())
    else:
        for r in rows:
            print(r)


def export_dpid_geotiff(gamma0_hh, gamma0_hv, dcp,
                        gslc_file_path, output_tiff_path, aoi_window=None):
    '''
    Export three DPID channels as a 3-band float32 GeoTIFF.

    Band 1: gamma0_HH  |  Band 2: gamma0_HV  |  Band 3: DCP ratio
    nodata=0.0  (marks water / masked pixels transparent in GIS tools).
    '''
    img_h, img_w = gamma0_hh.shape
    transform, clean_crs = _read_geo_meta(gslc_file_path, img_h, img_w, aoi_window)
    profile = {'driver': 'GTiff', 'height': img_h, 'width': img_w, 'count': 3,
               'dtype': rasterio.float32, 'crs': clean_crs, 'transform': transform,
               'nodata': 0.0, 'compress': 'lzw', 'tiled': True}
    print(f"Writing DPID GeoTIFF to: {output_tiff_path}")
    with rasterio.open(output_tiff_path, 'w', **profile) as dst:
        dst.write(gamma0_hh.astype(np.float32), 1)
        dst.write(gamma0_hv.astype(np.float32), 2)
        dst.write(dcp.astype(np.float32),        3)
    print("Done.")


# ─────────────────────────────────────────────────────────────────────────────
# Radar Forest Biomass Index
# ─────────────────────────────────────────────────────────────────────────────

def compute_rfbi(gamma0_hh, gamma0_hv):
    '''
    Compute the Radar Forest Biomass Index from calibrated gamma-nought arrays.

    RFBI = gamma0_HV / (gamma0_HH + gamma0_HV)  in [0, 1]

    Water (lowest 12% of SPAN) and urban pixels (top 5% HH, low DCP) are
    masked to 0.0 (nodata) before returning.

    Parameters
    ----------
    gamma0_hh, gamma0_hv : ndarray (2-D, float) -- speckle-filtered, calibrated

    Returns
    -------
    rfbi : ndarray (2-D, float32), values in [0, 1]; 0.0 = masked
    '''
    print("Computing RFBI = gamma0_HV / (gamma0_HH + gamma0_HV) ...")
    S0      = gamma0_hh + gamma0_hv
    S0_safe = np.where(S0 == 0, 1e-9, S0)
    rfbi    = gamma0_hv / S0_safe

    # Water mask: lowest 12% of total power
    water_cutoff = np.percentile(S0[np.isfinite(S0)], 12)
    water_mask   = S0 < water_cutoff

    # Urban mask: very bright co-pol AND low cross-pol fraction
    urban_cutoff = np.percentile(gamma0_hh[np.isfinite(gamma0_hh)], 95)
    urban_mask   = (gamma0_hh > urban_cutoff) & (rfbi < 0.3)

    rfbi[water_mask | urban_mask] = 0.0
    rfbi[~np.isfinite(rfbi)]      = 0.0
    rfbi = np.clip(rfbi, 0, 1)
    return rfbi.astype(np.float32)


def export_rfbi_geotiff(rfbi_array, gslc_file_path, output_tiff_path, aoi_window=None):
    '''
    Save the RFBI map as a single-band float32 GeoTIFF.
    nodata=0.0  (masked water / urban pixels rendered transparent in QGIS).
    '''
    img_h, img_w = rfbi_array.shape
    transform, clean_crs = _read_geo_meta(gslc_file_path, img_h, img_w, aoi_window)
    profile = {'driver': 'GTiff', 'height': img_h, 'width': img_w, 'count': 1,
               'dtype': rasterio.float32, 'crs': clean_crs, 'transform': transform,
               'nodata': 0.0, 'compress': 'lzw', 'tiled': True,
               'blockxsize': 256, 'blockysize': 256}
    print(f"Writing RFBI GeoTIFF to: {output_tiff_path}")
    with rasterio.open(output_tiff_path, 'w', **profile) as dst:
        dst.write(rfbi_array.astype(np.float32), 1)
    print("Done.")


# ─────────────────────────────────────────────────────────────────────────────
# Internal helper: read geographic metadata from the NISAR HDF5
# ─────────────────────────────────────────────────────────────────────────────

def _read_geo_meta(gslc_file_path, img_h, img_w, aoi_window):
    '''
    Return (affine_transform, crs_wkt) for a given AOI from a NISAR GSLC HDF5 file.
    Used by all export_*_geotiff functions to avoid code duplication.
    '''
    grid = "/science/LSAR/GSLC/grids/frequencyA/"
    with h5py.File(os.path.abspath(gslc_file_path), 'r') as f:
        x_coords = f[f"{grid}xCoordinates"][:]
        y_coords = f[f"{grid}yCoordinates"][:]
        x_sp     = abs(float(x_coords[1] - x_coords[0]))
        y_sp     = abs(float(y_coords[1] - y_coords[0]))
        raw_proj = f[f"{grid}projection"][()]
        proj_str = raw_proj.decode('utf-8') if isinstance(raw_proj, bytes) else str(raw_proj)

    r0, r1, c0, c1 = aoi_window if aoi_window else (0, img_h, 0, img_w)
    geo_x = min(float(x_coords[c0]), float(x_coords[c1 - 1]))
    geo_y = max(float(y_coords[r0]), float(y_coords[r1 - 1]))
    transform = from_origin(geo_x, geo_y, x_sp, y_sp)
    try:
        clean_crs = CRS.from_user_input(proj_str).to_wkt()
    except Exception:
        print("  Warning: CRS parsing failed, falling back to EPSG:4326.")
        clean_crs = "EPSG:4326"
    return transform, clean_crs
