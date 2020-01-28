'''
    Example flask webserver using folium
'''
# pylint: disable=invalid-name, protected-access, global-statement
from flask import Flask
from flask import render_template
from flask import Markup
import folium
from folium.plugins import HeatMap
from folium.plugins import MarkerCluster

import pandas as pd


app = Flask(__name__)


# will hold fatal crash data
fatal = None


def add_heat_map(folium_map: folium.Map) -> None:
    '''
    add_heat_map: add heat map for fatal crashes

    Parameters:
    folium_map: map to which heat map is to be added as Layer

    Return:
    None

    Side Effects:
    Adds heat map Layer to input map
    '''

    global fatal
    lat = list(fatal['Crash_Latitude_GDA94'])
    lng = list(fatal['Crash_Longitude_GDA94'])

    heat_in = [[y, x] for y, x in zip(lat, lng)]

    HeatMap(
        data=heat_in, name='Heat Map', show=False, control=True, min_opacity=0.5
    ).add_to(folium_map)


# end add_heat_map


def add_markers(folium_map: folium.Map) -> None:
    '''
    annotate_map: add fatal crash markers to map

    Parameters:
    folium_map: map to which markers are to be added as Layer

    Returns:
    None

    Side Effects:
    Adds markers to input map as a Layer

    '''
    global fatal
    lat = list(fatal['Crash_Latitude_GDA94'])
    lng = list(fatal['Crash_Longitude_GDA94'])
    dead_count = list(fatal['Count_Casualty_Fatality'])
    crash_nature = list(fatal['Crash_Nature'])
    crash_type = list(fatal['Crash_Type'])

    FATAL_MARKER_SIZE = 10
    FATAL_MARKER_FILL_OPACITY = 0.25

    # create a FeatureGroup so Crashes can be turned off
    fatal_fg = folium.FeatureGroup(name='Fatal Crashes', show=True)

    # for each fatal crash, add marker to layer
    # marker is translucent so zoom out will look ok

    for marker_y, marker_x, marker_dc, marker_cn, marker_ct in zip(
        lat, lng, dead_count, crash_nature, crash_type
    ):

        circ_mkr = folium.CircleMarker(
            location=[marker_y, marker_x],
            radius=FATAL_MARKER_SIZE,
            color='red',
            fill=True,
            fill_color='red',
            fillOpacity=FATAL_MARKER_FILL_OPACITY,
            opacity=FATAL_MARKER_FILL_OPACITY,\
            tooltip=f'{marker_dc} Dead',
            popup=marker_cn,
        )
        circ_mkr.add_to(fatal_fg)
    # end for

    # add unclustered markers to map
    fatal_fg.add_to(folium_map)

    return None


# end add_markers


def add_clusters(folium_map: folium.Map) -> None:
    '''
    annotate_map: add clustered fatal crash markers to map

    Parameters:
    folium_map: map to which markers are to be added as Layer

    Returns:
    None

    Side Effects:
    Adds markers to input map as a Layer

    '''
    global fatal
    lat = list(fatal['Crash_Latitude_GDA94'])
    lng = list(fatal['Crash_Longitude_GDA94'])
    dead_count = list(fatal['Count_Casualty_Fatality'])
    crash_nature = list(fatal['Crash_Nature'])
    crash_type = list(fatal['Crash_Type'])

    FATAL_MARKER_SIZE = 10
    FATAL_MARKER_FILL_OPACITY = 0.25

    # create a marker cluster layer
    clusters = MarkerCluster(name='Clustered Markers', show=False, control=True)

    # for each fatal crash, add marker to layer
    # marker is translucent so zoom out will look ok

    for marker_y, marker_x, marker_dc, marker_cn, marker_ct in zip(
        lat, lng, dead_count, crash_nature, crash_type
    ):
        circ_mkr = folium.CircleMarker(
            location=[marker_y, marker_x],
            radius=FATAL_MARKER_SIZE,
            color='red',
            fill=True,
            fill_color='red',
            fillOpacity=FATAL_MARKER_FILL_OPACITY,
            opacity=FATAL_MARKER_FILL_OPACITY,
            tooltip=f'{marker_dc} Dead',
            popup=marker_cn,
        )

        circ_mkr.add_to(clusters)
    # end for

    # add clustered markers to map
    clusters.add_to(folium_map)

    return None


# end add_clusters


@app.route('/')
def index() -> str:
    '''
    index: returns home page of example server, with welcoming text
    '''
    return render_template(
        'index.html',
        map_div='',
        hdr_txt='',
        script_txt='',
        title='QLD Crash Map',
        folium_version=folium.__version__,
    )


# end index

@app.route('/_ah/warmup')
def warmup():
    """Warm up an instance of the app."""
    # load fatal crash data
    print('data loading ...')
    load_crash_data()
    print('data loaded')


@app.route('/crashmap')
def crashmap() -> str:
    '''
    crashmap: generates a webpage holding a leaflet / folium map
    '''
    start_coords = (-26.52, 153.09)
    folium_map = folium.Map(
        tiles=None,
        location=start_coords,
        zoom_start=13,
        width='80%',
        height='80%',
        control_scale=True,
    )

    # support two basemaps
    folium.TileLayer(tiles='OpenStreetMap', name='Open Street Map', show=True).add_to(
        folium_map
    )
    folium.TileLayer(tiles='stamentoner', name='Black/White Map', show=False).add_to(
        folium_map
    )

    # add un-clustered markers layer
    add_markers(folium_map)

    # add the clustered fatal crash markers layer
    add_clusters(folium_map)

    # add heat map layer
    add_heat_map(folium_map)

    # add control to pick basemap, layers to show
    folium.LayerControl().add_to(folium_map)

    # Extract the components of the web map

    #
    #  The HTML to create a <div> and <iframe> to hold the map
    #
    #  The header text to get styles, scripts, etc
    #
    #  The scripts needed to run

    # first, force map to render as HTML, for us to dissect
    _ = folium_map._repr_html_()

    # get definition of map in body
    map_div = Markup(folium_map.get_root().html.render())

    # html to be included in header
    hdr_txt = Markup(folium_map.get_root().header.render())

    # html to be included in <script>
    script_txt = Markup(folium_map.get_root().script.render())

    return render_template(
        'crashmap.html',
        map_div=map_div,
        hdr_txt=hdr_txt,
        script_txt=script_txt,
        title='QLD Crash Map Annotated',
    )


# end crashmap


def load_crash_data() -> pd.DataFrame:
    '''
    load_crash_data: load crash dataset into pandas DataFrame

    Parameters:
    None

    Returns:
    Pandas DataFrame

    Side Effects:
    updates global variable fatal with DataFrame contents
    '''
    global fatal
    crash_path = 'locations.csv'

    #  tell pandas that PostCodes are not integers, but strings
    crashes = pd.read_csv(crash_path, dtype={'Loc_Post_Code': str})
    fatal = crashes[crashes["Crash_Severity"] == 'Fatal']

    return fatal


# end load_crash

if __name__ == '__main__':
    # load fatal crash data
    print('data loading ...')
    load_crash_data()
    print('data loaded')

    app.run(host='127.0.0.1', port=8080)
