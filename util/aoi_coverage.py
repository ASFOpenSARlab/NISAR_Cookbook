from ipyleaflet import Map, Polygon, Polyline, basemap_to_tiles, basemaps, TileLayer, WidgetControl
import ipywidgets as widgets
from itertools import cycle
from shapely import wkt


def plot_aoi_coverage(gpolygons, aoi_wkt, product_type):
    colors = cycle([
        "yellow",
        "cyan",
        "lime",
        "magenta",
        "orange",
        "blue",
    ])
    
    all_lats = []
    all_lons = []
    
    m = Map(zoom=7)
    m.layout.width = "100%"
    m.layout.height = "800px"
    m.add(basemap_to_tiles(basemaps.Esri.WorldImagery))
    
    labels = TileLayer(
        url="https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        attribution="Esri",
        name="Esri Boundaries and Places",
    )
    m.add(labels)
    
    for gpolygon, color in zip(gpolygons, colors):
        points = gpolygon["Boundary"]["Points"]
    
        lats = [p["Latitude"] for p in points]
        lons = [p["Longitude"] for p in points]
    
        all_lats.extend(lats)
        all_lons.extend(lons)
    
        bbox_locations = [
            [min(lats), min(lons)],
            [min(lats), max(lons)],
            [max(lats), max(lons)],
            [max(lats), min(lons)],
            [min(lats), min(lons)],
        ]
    
        m.add(
            Polygon(
                locations=bbox_locations,
                color=color,
                fill_color=color,
                fill_opacity=0.15,
                weight=2,
                name=f"Extent {color}",
            )
        )
    
    subset_poly = wkt.loads(aoi_wkt)
    subset_locations = [[lat, lon] for lon, lat in subset_poly.exterior.coords]
    
    m.add(
        Polyline(
            locations=subset_locations,
            color="red",
            weight=2,
            opacity=0.9,
            dash_array="4,4",
            fill=False,
        )
    )
    
    legend = widgets.HTML(
        value=f"""
        <div style="
            background-color: rgba(255,255,255,0.5);
            padding: 8px 10px;
            border: 1px solid rgba(120,120,120,0.8);
            border-radius: 4px;
            font-size: 13px;
            color: #222;
            box-shadow: 0 1px 4px rgba(0,0,0,0.3);
            backdrop-filter: blur(2px);
        ">
            <div style="font-weight: 600; margin-bottom: 6px;">Legend</div>
    
            <div style="display:flex; align-items:center; gap:6px; margin-bottom:6px;">
                <span style="display:inline-block; width:28px; border-top:2px dashed red;"></span>
                <span>AOI</span>
            </div>
    
            <div style="display:flex; align-items:center; gap:6px;">
                <span style="white-space: nowrap;">
                    <span style="display:inline-block;width:8px;height:12px;border:1px solid yellow;"></span>
                    <span style="display:inline-block;width:8px;height:12px;border:1px solid cyan;"></span>
                    <span style="display:inline-block;width:8px;height:12px;border:1px solid lime;"></span>
                    <span style="display:inline-block;width:8px;height:12px;border:1px solid magenta;"></span>
                    <span style="display:inline-block;width:8px;height:12px;border:1px solid orange;"></span>
                    <span style="display:inline-block;width:8px;height:12px;border:1px solid blue;"></span>
                </span>
                <span>NISAR {product_type} extents</span>
            </div>
        </div>
        """,
        layout=widgets.Layout(
            background_color="transparent",
            border="none",
            padding="0px",
            margin="0px",
        ),
    )
    
    legend_control = WidgetControl(
        widget=legend,
        position="bottomright",
        transparent_bg=True,
    )
    
    m.add(legend_control)
    
    m.center = [
        (min(all_lats) + max(all_lats)) / 2,
        (min(all_lons) + max(all_lons)) / 2,
    ]
    
    m.fit_bounds([
        [min(all_lats), min(all_lons)],
        [max(all_lats), max(all_lons)],
    ])
    
    return m