import panel as pn
import holoviews as hv
import hvplot.xarray


def fr_view(omega_web, quality_web):
    """Create an interactive Faraday rotation and quality map.
    
    omega_web: Faraday Rotation Estimate raster in web-mercator projection
    quality_web: Quality metric raster in web-mercator projection
    """

    xlim = (float(omega_web.x.min()), float(omega_web.x.max()))
    ylim = (float(omega_web.y.min()), float(omega_web.y.max()))

    # Esri basemap
    tiles = hv.element.tiles.EsriImagery().opts(
        xlim=xlim,
        ylim=ylim,
        frame_width=700,
        frame_height=500,
        active_tools=["wheel_zoom"],
    )

    # Raster plotting configurations
    image_kwargs = [
        # Faraday Rotation
        {
            "x": "x",
            "y": "y",
            "cmap": "RdBu_r",
            "clim": (-6, 6),
            "colorbar": True,
            "frame_width": 700,
            "frame_height": 500,
        },
        # Quality metric
        {
            "x": "x",
            "y": "y",
            "cmap": "viridis",
            "clim": (0, 1),
            "colorbar": True,
            "frame_width": 700,
            "frame_height": 500,
        },
    ]

    titles = ["Faraday Rotation", "Faraday Rotation Quality"]

    opts_kwargs = {
        "xlim": xlim,
        "ylim": ylim,
    }

    # Raster selection button
    display_mode = pn.widgets.RadioButtonGroup(
        name="Display",
        options={
            "Faraday Rotation": 0,
            "Quality": 1,
        },
        value=0,
    )

    # Alpha slider
    alpha = pn.widgets.FloatSlider(
        name="Alpha",
        start=0.0,
        end=1.0,
        step=0.05,
        value=1.0,
    )

    def plot(selected, alpha):
        layer = [omega_web, quality_web][selected].hvplot.image(
            **image_kwargs[selected]
        ).opts(
            **opts_kwargs,
            alpha=alpha,
        )

        return (tiles * layer).opts(title=titles[selected])

    view = pn.bind(
        plot,
        selected=display_mode,
        alpha=alpha,
    )

    layout = pn.Column(display_mode, alpha, view)
    
    return layout.embed(
        states={
            display_mode: [0, 1],
            alpha: [0.0, 0.25, 0.5, 0.75, 1.0],
        },
        max_states=10,
        json=False,
    )
    