"""
nisar_plot_utils.py
===================
Shared plotting utilities for NISAR dual-pol SAR analysis notebooks.

Extracted from Pottier_or_Raney-v0.4.ipynb so that plotting code can be
reused across notebooks without copy-pasting.

Functions
---------
plot_halpha_maps           – spatial maps of H and alpha from Cloude-Pottier
plot_decomposition_histograms – histograms of H and alpha distributions
plot_cloude_pottier_zones  – 9-zone H/alpha classification map
plot_dual_pol_rgb          – generic 3-channel false-colour composite
plot_dual_pol_classification – 5-class Dual-Pol Intensity classification map
plot_decompositions_comparison – side-by-side H/alpha vs. DPID comparison
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch


# ---------------------------------------------------------------------------
# 1. Cloude-Pottier H / alpha spatial maps
# ---------------------------------------------------------------------------

def plot_halpha_maps(H, alpha_deg):
    """
    Display side-by-side spatial images of Polarimetric Entropy (H) and
    Mean Scattering Alpha Angle (degrees) from the Cloude-Pottier decomposition.

    Parameters
    ----------
    H : ndarray (2-D, float)
        Polarimetric entropy, values in [0, 1].
    alpha_deg : ndarray (2-D, float)
        Mean scattering angle in degrees, values in [0, 90].
    """
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))

    im0 = ax[0].imshow(H, cmap='viridis', vmin=0, vmax=1, origin='upper')
    ax[0].set_title("Polarimetric Entropy (H)", fontsize=13)
    fig.colorbar(im0, ax=ax[0], label="Randomness  (0 = pure, 1 = random)")
    ax[0].axis('off')

    im1 = ax[1].imshow(alpha_deg, cmap='jet', vmin=0, vmax=90, origin='upper')
    ax[1].set_title(r"Mean Scattering Angle ($\alpha$)", fontsize=13)
    fig.colorbar(im1, ax=ax[1], label="Degrees (0° – 90°)")
    ax[1].axis('off')

    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
# 2. H / alpha histograms
# ---------------------------------------------------------------------------

def plot_decomposition_histograms(H, alpha_deg, step=5):
    """
    Plot frequency distributions of Polarimetric Entropy and Mean Scattering
    Alpha Angle side by side.

    Parameters
    ----------
    H : ndarray
        Entropy array (values in [0, 1]).
    alpha_deg : ndarray
        Alpha angle array (values in [0, 90]).
    step : int
        Sub-sampling step for faster rendering of large arrays.
    """
    H_flat    = H[::step, ::step].flatten()
    alpha_flat = alpha_deg[::step, ::step].flatten()

    H_clean     = H_flat[np.isfinite(H_flat)]
    alpha_clean = alpha_flat[np.isfinite(alpha_flat)]

    fig, ax = plt.subplots(1, 2, figsize=(14, 5))

    ax[0].hist(H_clean, bins=100, range=(0, 1), color='#21918c',
               edgecolor='black', alpha=0.75, density=True)
    ax[0].set_title("Polarimetric Entropy ($H$) Distribution", fontsize=13)
    ax[0].set_xlabel("Entropy (0 = deterministic, 1 = random)", fontsize=11)
    ax[0].set_ylabel("Probability Density", fontsize=11)
    ax[0].grid(True, linestyle='--', alpha=0.5)

    ax[1].hist(alpha_clean, bins=90, range=(0, 90), color='#d62728',
               edgecolor='black', alpha=0.75, density=True)
    ax[1].set_title(r"Mean Scattering Alpha ($\alpha$) Distribution", fontsize=13)
    ax[1].set_xlabel(r"Alpha Angle (degrees)", fontsize=11)
    ax[1].set_ylabel("Probability Density", fontsize=11)
    ax[1].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
# 3. Cloude-Pottier 9-zone classification map
# ---------------------------------------------------------------------------

# Palette: index 0 = background, indices 1-9 = the nine H/alpha zones
_CP_COLORS = [
    '#111111',  # 0: Background / unclassified (near-black)
    '#D50000',  # 1: High-H double-bounce
    '#1B5E20',  # 2: High-H volume
    '#0D47A1',  # 3: High-H complex surface
    '#FF6D00',  # 4: Medium-H double-bounce
    '#AEEA00',  # 5: Medium-H volume / vegetation
    '#00B8D4',  # 6: Medium-H surface
    '#FF4081',  # 7: Low-H double-bounce
    '#FFD600',  # 8: Low-H dipole / oriented crops
    '#F5F5F5',  # 9: Low-H surface / calm water
]

_CP_LEGEND_LABELS = [
    ('Z1', '#D50000', 'High-H Double-Bounce (flooded forest / dense urban)'),
    ('Z2', '#1B5E20', 'High-H Volume (dense forest canopy)'),
    ('Z3', '#0D47A1', 'High-H Surface (complex rough surfaces)'),
    ('Z4', '#FF6D00', 'Medium-H Double-Bounce (urban / oriented structures)'),
    ('Z5', '#AEEA00', 'Medium-H Volume (vegetation / crops)'),
    ('Z6', '#00B8D4', 'Medium-H Surface (rough soil / moderate water)'),
    ('Z7', '#FF4081', 'Low-H Double-Bounce (isolated buildings)'),
    ('Z8', '#FFD600', 'Low-H Dipole (sparse veg / oriented crops)'),
    ('Z9', '#F5F5F5', 'Low-H Surface (calm water / smooth bare ground)'),
]


def plot_cloude_pottier_zones(zones, title="Dual-Pol Cloude-Pottier 9-Zone Map"):
    """
    Render a high-contrast map of the 9-zone H/alpha classification.

    Parameters
    ----------
    zones : ndarray (2-D, uint8)
        Integer zone labels in {0, …, 9}.
    title : str
        Figure title.
    """
    cmap = ListedColormap(_CP_COLORS)

    plt.figure(figsize=(14, 11), facecolor='#1E1E1E')
    plt.imshow(zones, cmap=cmap, vmin=0, vmax=9, origin='upper')
    plt.title(title, color='white', fontsize=14, pad=15)
    plt.axis('off')

    patches = [Patch(facecolor=c, label=f'{z}: {lbl}')
               for z, c, lbl in _CP_LEGEND_LABELS]
    legend = plt.legend(handles=patches, loc='center left',
                        bbox_to_anchor=(1.02, 0.5),
                        facecolor='#2D2D2D', edgecolor='none')
    for t in legend.get_texts():
        t.set_color('white')

    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
# 4. Generic 3-channel false-colour composite
# ---------------------------------------------------------------------------

def plot_dual_pol_rgb(R, G, B, title="Dual-Pol RGB Composite"):
    """
    Display a three-channel false-colour composite after percentile
    normalization to [0, 1].

    Parameters
    ----------
    R, G, B : ndarray (2-D)
        Raw (un-normalised) channel arrays.
    title : str
        Figure title.
    """
    def _norm(ch):
        clean = ch[np.isfinite(ch)]
        if clean.size == 0:
            return np.zeros_like(ch)
        lo, hi = np.percentile(clean, 2), np.percentile(clean, 98)
        denom = hi - lo if hi > lo else 1.0
        return np.clip((ch - lo) / denom, 0, 1)

    rgb = np.dstack((_norm(R), _norm(G), _norm(B)))
    plt.figure(figsize=(12, 10))
    plt.imshow(rgb, origin='upper')
    plt.title(title, fontsize=13)
    plt.axis('off')
    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
# 5. Dual-Pol Intensity Decomposition classification map
# ---------------------------------------------------------------------------

_DPID_COLORS = [
    '#111111',  # 0: Background
    '#0D47A1',  # 1: Calm water / specular surface (very low σ°_span)
    '#F5F5F5',  # 2: Bare soil / smooth surface (high HH, low HV)
    '#1B5E20',  # 3: Dense vegetation / forest (high HV, high DCP)
    '#FF6D00',  # 4: Urban / built-up (very high HH, moderate HV)
    '#00B8D4',  # 5: Wetlands / flooded vegetation (high HH + HV)
]

_DPID_LEGEND_LABELS = [
    ('#0D47A1', 'Calm Water / Specular Surface'),
    ('#F5F5F5', 'Bare Soil / Smooth Open Land'),
    ('#1B5E20', 'Dense Vegetation / Forest'),
    ('#FF6D00', 'Urban / Built-up Structures'),
    ('#00B8D4', 'Wetlands / Flooded Vegetation'),
]


def plot_dual_pol_classification(classes,
                                 title="Dual-Pol Intensity Decomposition Classification"):
    """
    Render the Dual-Pol Intensity Decomposition (DPID) 5-class land-cover map.

    Parameters
    ----------
    classes : ndarray (2-D, uint8)
        Integer class labels in {0, …, 5}.
    title : str
        Figure title.
    """
    cmap = ListedColormap(_DPID_COLORS)

    plt.figure(figsize=(14, 11), facecolor='#1E1E1E')
    plt.imshow(classes, cmap=cmap, vmin=0, vmax=5, origin='upper')
    plt.title(title, color='white', fontsize=14, pad=15)
    plt.axis('off')

    patches = [Patch(facecolor=c, label=lbl)
               for c, lbl in _DPID_LEGEND_LABELS]
    legend = plt.legend(handles=patches, loc='center left',
                        bbox_to_anchor=(1.02, 0.5),
                        facecolor='#2D2D2D', edgecolor='none')
    for t in legend.get_texts():
        t.set_color('white')

    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
# 6. Side-by-side comparison: Cloude-Pottier zones vs. DPID RGB
# ---------------------------------------------------------------------------

def plot_decompositions_comparison(dpid_R, dpid_G, dpid_B, cp_zones):
    """
    Display the DPID false-colour composite alongside the Cloude-Pottier
    9-zone classification in a single figure with a shared legend.

    Parameters
    ----------
    dpid_R, dpid_G, dpid_B : ndarray
        Raw DPID channels (γ°_HH, γ°_HV, γ°_HV/γ°_HH ratio).
    cp_zones : ndarray (2-D, uint8)
        Cloude-Pottier classification zones.
    """
    def _norm(ch):
        clean = ch[np.isfinite(ch)]
        if clean.size == 0:
            return np.zeros_like(ch)
        lo, hi = np.percentile(clean, 2), np.percentile(clean, 98)
        denom = hi - lo if hi > lo else 1.0
        return np.clip((ch - lo) / denom, 0, 1)

    dpid_rgb = np.dstack((_norm(dpid_R), _norm(dpid_G), _norm(dpid_B)))
    cp_cmap  = ListedColormap(_CP_COLORS)

    fig, ax = plt.subplots(2, 2, figsize=(20, 12),
                           gridspec_kw={'height_ratios': [1, 0.22]})

    ax[0, 0].imshow(dpid_rgb, origin='upper')
    ax[0, 0].set_title(
        "Dual-Pol Intensity Decomposition (DPID)\n"
        "R: σ°_HH  |  G: σ°_HV  |  B: σ°_HH / σ°_HV",
        fontsize=13, pad=10)
    ax[0, 0].axis('off')

    ax[0, 1].imshow(cp_zones, cmap=cp_cmap, vmin=0, vmax=9, origin='upper')
    ax[0, 1].set_title(
        "Adapted Dual-Pol Cloude-Pottier\n9-Zone Unsupervised Classification",
        fontsize=13, pad=10)
    ax[0, 1].axis('off')

    ax[1, 0].axis('off')
    ax[1, 1].axis('off')

    patches = [Patch(facecolor=c, edgecolor='black', linewidth=0.5,
                     label=f'{z}: {lbl}')
               for z, c, lbl in _CP_LEGEND_LABELS]
    fig.legend(handles=patches, loc='lower center', ncol=3,
               frameon=True, facecolor='#FAFAFA', edgecolor='#CCCCCC',
               fontsize=10, title='Cloude-Pottier Classification Zones',
               title_fontsize=12, labelspacing=1.0, columnspacing=1.5)

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.show()


# ---------------------------------------------------------------------------
# 7. GSLC full-scene RGB overview
# ---------------------------------------------------------------------------

def plot_gslc_overview(gslc_file_path, step=20):
    """
    Read the full GSLC scene at reduced resolution and display a false-colour
    RGB composite for quick scene orientation.

    Channel mapping
    ---------------
    R = gamma0_HH in dB  (co-pol: surfaces and double-bounce)
    G = gamma0_HV in dB  (cross-pol: volume / vegetation)
    B = HV/HH ratio in dB (Degree of Cross-Polarization)

    Parameters
    ----------
    gslc_file_path : str
        Path to the NISAR GSLC HDF5 file.
    step : int
        Pixel decimation factor (step=20 reads 1 in 20 pixels in each direction).
    """
    import os, h5py, hdf5plugin
    abs_path  = os.path.abspath(gslc_file_path)
    base_path = "/science/LSAR/GSLC/grids/frequencyA/"

    print(f"Opening file and downsampling by factor {step}...")
    with h5py.File(abs_path, 'r') as f:
        hh_amp = np.abs(f[f'{base_path}HH'][::step, ::step])
        hv_amp = np.abs(f[f'{base_path}HV'][::step, ::step])

    hh_amp = np.where(hh_amp <= 0, 1e-6, hh_amp)
    hv_amp = np.where(hv_amp <= 0, 1e-6, hv_amp)

    R_db    = 20 * np.log10(hh_amp)
    G_db    = 20 * np.log10(hv_amp)
    B_ratio = 20 * np.log10(hv_amp / hh_amp)

    def _pct_norm(ch, lo=2, hi=98):
        clean = ch[np.isfinite(ch)]
        if clean.size == 0:
            return np.zeros_like(ch)
        cmin, cmax = np.percentile(clean, lo), np.percentile(clean, hi)
        denom = (cmax - cmin) if cmax > cmin else 1.0
        out = np.clip((ch - cmin) / denom, 0, 1)
        out[~np.isfinite(out)] = 0.0
        return out

    rgb = np.dstack((_pct_norm(R_db), _pct_norm(G_db), _pct_norm(B_ratio)))
    plt.figure(figsize=(12, 10))
    plt.imshow(rgb, origin='upper')
    plt.title(
        f"NISAR Dual-Pol Full RGB Overview  (1:{step} downsampling)\n"
        "Red = gamma_HH  |  Green = gamma_HV  |  Blue = HV/HH ratio")
    plt.xlabel(f"Columns  (x{step} pixels per tick)")
    plt.ylabel(f"Rows     (x{step} pixels per tick)")
    plt.grid(False)
    plt.show()


# ---------------------------------------------------------------------------
# 8. Stokes parameter density scatter plot
# ---------------------------------------------------------------------------

def plot_stokes_distribution(gslc_file_path, window_size=5,
                             aoi_window=None, step=20):
    """
    Compute Stokes parameters S1 and S2 and display their joint density as a
    hexbin scatter plot.

    For a linear HH/HV system:
      S1 = gamma0_HH - gamma0_HV  (co-pol excess; >0 = co-pol dominated)
      S2 = 2 Re<S_HH * S_HV*>    (real HH-HV cross-correlation)

    The hexbin density plot reveals dominant polarimetric regimes:
      S1 >> 0 (right): surface scattering (bare soil, smooth water)
      S1 ~  0 (centre): balanced / volume scattering (dense forest)
      |S2| large: coherent cross-channel correlation (oriented structures)

    Parameters
    ----------
    gslc_file_path : str    -- Path to the NISAR GSLC HDF5 file
    window_size : int       -- Speckle filter window for intensity smoothing
    aoi_window : tuple/None -- (row_start, row_end, col_start, col_end)
    step : int              -- Sub-sampling step (step=20 uses 1 in 400 pixels)
    """
    from nisar_polsar import refined_lee_filter
    import os, h5py, hdf5plugin

    abs_path  = os.path.abspath(gslc_file_path)
    grid_path = "/science/LSAR/GSLC/grids/frequencyA/"

    print(f"Reading sub-sampled data (1 in {step}^2 = 1 in {step**2} pixels)...")
    with h5py.File(abs_path, 'r') as f:
        full_shape = f[f'{grid_path}HH'].shape
        r0, r1, c0, c1 = aoi_window if aoi_window else (0, full_shape[0], 0, full_shape[1])
        S_hh = f[f'{grid_path}HH'][r0:r1:step, c0:c1:step]
        S_hv = f[f'{grid_path}HV'][r0:r1:step, c0:c1:step]

    I_hh = refined_lee_filter(np.real(S_hh * np.conj(S_hh)), window_size)
    I_hv = refined_lee_filter(np.real(S_hv * np.conj(S_hv)), window_size)
    S1 = (I_hh - I_hv).flatten()
    S2 = (2 * refined_lee_filter(np.real(S_hh * np.conj(S_hv)), window_size)).flatten()

    valid = np.isfinite(S1) & np.isfinite(S2)
    S1c, S2c = S1[valid], S2[valid]
    print(f"Plotting {S1c.size:,} valid polarisation states...")

    plt.figure(figsize=(10, 8))
    plt.hexbin(S1c, S2c, gridsize=100, cmap='inferno', mincnt=1, bins='log')
    plt.axhline(0, color='white', linestyle='--', alpha=0.5)
    plt.axvline(0, color='white', linestyle='--', alpha=0.5)
    plt.title(r"Stokes Polarisation State Distribution ($S_1$ vs $S_2$)", fontsize=14)
    plt.xlabel(r"$S_1$ = gamma_HH - gamma_HV    (co-pol excess)", fontsize=11)
    plt.ylabel(r"$S_2$ = 2 Re<$S_{HH} S_{HV}^*$>    (HH-HV cross-correlation)", fontsize=11)
    plt.colorbar(label='log10(Pixel count per hex bin)')
    plt.grid(True, linestyle=':', alpha=0.3)
    plt.show()
