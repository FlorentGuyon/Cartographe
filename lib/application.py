# -*- coding: utf-8 -*-

from . import config
import os
import plotly.graph_objects as go
from dash import Dash
from dash.dependencies import Output, Input
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_cytoscape as cyto
import dash_leaflet as dl
import dash_leaflet.express as dlx
from threading import Thread


class NetworkChart():

    layout = None
    nodes = None
    edges = None
    compounds = None
    classes = None

    def __init__(self):
        """Create an empty network graph"""
        self.nodes = []
        self.edges = []
        self.compounds = []
        self.classes = []
        # Load the extended set of network layouts
        cyto.load_extra_layouts()
        # https://js.cytoscape.org/
        self.layout = cyto.Cytoscape(
            id="network",
            layout={
                # https://js.cytoscape.org/#demos
                'name': config.get_config().application.components.network_chart.layouts[6],
                'fit': True,
            },
            responsive=True,
            elements=[],
            style={'width': '100%', 'height': '600px'},
            stylesheet=[
                # https://js.cytoscape.org/#style/node-body
                {'selector': 'node', 'style': {
                    'color': '#D1CDC7',
                    'background-color': 'data(color)',
                    'animate': True,
                    'border-opacity': 0,
                    'padding': '15px',
                    'compound-sizing-wrt-labels': 'include',
                    'text-max-width': '150px',
                    'text-wrap': 'wrap',
                    'text-margin-y': '-10px',
                    'text-background-color': '#181a1b',
                    'text-background-opacity': 0.5,
                    'text-background-padding': '5px',
                    'min-zoomed-font-size': '16px',
                    'text-events': 'yes'
                }},
                {'selector': 'node:active', 'style': {
                    'content': 'data(label)',
                }},
                {'selector': 'edge', 'style': {
                    'color': '#D1CDC7',
                    'line-color': 'light-gray',
                    'width': '2px',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'target-text-offset': '20px',
                    'target-text-margin-y': '-15px',
                    'text-background-color': '#181a1b',
                    'text-background-opacity': 0.5,
                    'text-background-padding': '5px',
                    'min-zoomed-font-size': '16px',
                    'text-events': 'yes'
                }},
                {'selector': 'edge:active', 'style': {
                    'target-label': 'data(weight)',
                }},
            ]
        )

        icons_path = config.get_config().application.components.network_chart.icons_path
        for file in os.listdir(icons_path):
            file_name = file.split('.')[0]
            self.classes.append(file_name)
            selector = {'selector': f".{file_name}", 'style': {'background-image': f'url({icons_path}{file})',
                                                               'background-fit': 'cover',
                                                               'background-opacity': 0}}
            self.layout.stylesheet.append(selector)

    def add_node(self, data):
        """Add a new node to the graph"""
        node = {'data': {'id': data["ip_addr"],
                         'label': data["hostname"],
                         'parent': None},
                'classes': "computer"}
        if data["ip_addr"].split('.')[-1] == '1':
            node["classes"] = "router"
        for name in self.classes:
            if name in data["hostname"]:
                node["classes"] = name
        self.nodes.append(node)

    def add_compound(self, data):
        """Not used yet"""
        node = {'data': {'id': None, 'label': None,
                         'parent': None, 'color': None}, 'classes': None}
        self.compounds.append(compound)

    def add_edge(self, data):
        """Add an edge between two nodes"""
        edge = {'data': {'source': data["ip_src"],
                         'target': data["ip_dst"],
                         'weight': None},
                'classes': None}
        self.edges.append(edge)

    def get_data(self):
        """Return the data needed for the graph update"""
        return self.nodes + self.edges + self.compounds


class MapChart():

    layout = None
    points = None

    def __init__(self):
        """Create an empty world map"""
        self.points = []

        map_info = dbc.Toast(
            [html.P("This is the content of the toast", className="mb-0")],
            header="This is the header",
            id="map_info",
            style={"z-index": "1000", "right": 0, "margin": "10px", "position": "absolute",
                   "background-color": "#262629", "opacity": 0.9, "border": "1px solid #555", "color": "#dbd6d6"}
        )

        # https://dash-leaflet.herokuapp.com/#choropleth_us
        # https://leafletjs.com/reference-1.3.4.html#geojson
        countries = dl.GeoJSON(
            url=f"url({config.get_config().application.components.map_chart.countries})",
            options=dict(
                style=dict(opacity=0, fillOpacity=0)),
            zoomToBoundsOnClick=True,
            hoverStyle=dict(opacity=1, color='#666', dashArray='',
                            fillOpacity=0.25, weight=1)
        )

        # https://dash-leaflet.herokuapp.com/
        self.layout = dl.Map([
            dl.TileLayer(
                url='https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png',
                minZoom=2,
                maxZoom=25,
                attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> ',
            ),
            # dl.LocateControl(startDirectly=True, options={'locateOptions': {'enableHighAccuracy': True}}),
            countries,
            dl.GeoJSON(
                data=None,
                format="geobuf",
                id="geolocation",
                hoverStyle=dict(
                    weight=5,
                    color='red',
                    dashArray=''
                )
            ),
            map_info
        ],
            zoom=2,
            center=(32, 10),
            style={'width': '100%', 'height': '500px'}
        )

    def add_point(self, data):
        """Add a pin to the map"""
        if "latitude" in data.keys() and "longitude" in data.keys():
            self.points.append(
                {'lat': data["latitude"],
                 'lon': data["longitude"],
                 'data': data})

    def get_data(self):
        """Convert and return the data needed for the map"""
        return dlx.geojson_to_geobuf(dlx.dicts_to_geojson(self.points))


dash = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], update_title=None)
network_chart = NetworkChart()
map_chart = MapChart()


class Application(Thread):

    running = None
    queue = None

    def __init__(self, queue):
        """Generate a ready to run WEB server hosting a custom web site"""
        Thread.__init__(self, daemon=True)
        self.queue = queue
        self.running = False

        charts_update_clock = dcc.Interval(
            id='charts_update_clock',
            interval=config.get_config().application.components.update_interval)

        ##########################################################################
        #                            L  A  Y  O  U  T                            #
        ##########################################################################

        #       -------------------------------------------------
        #       |***********************************************|
        #       |***********************************************|
        #       |                                               |
        #       |                                               |
        #       |                                               |
        #       |                                               |
        #       |                                               |
        #       |                                               |
        #       |                                               |
        #       |                                               |
        #       |                                               |
        #       -------------------------------------------------
        #
        navbar = dbc.Navbar(
            [
                html.A(
                    [
                        html.Span(html.Img(src=f'{config.get_config().application.icons_path}icon.png',
                                           width=30, className="logo"), className="mr-2"),
                        dbc.NavbarBrand(config.get_config().application.title,
                                        className="ml-2")
                    ],
                    href="#"
                ),
                dbc.NavbarToggler(id="navbar-toggler"),
            ],
            className="navbar sticky-top flex-md-nowrap shadow",
            color="#212325",
            dark=True,
        )

        #       -------------------------------------------------
        #       |                                               |
        #       |                                               |
        #       |*********                                      |
        #       |*********                                      |
        #       |*********                                      |
        #       |*********                                      |
        #       |*********                                      |
        #       |*********                                      |
        #       |*********                                      |
        #       |*********                                      |
        #       |*********                                      |
        #       -------------------------------------------------
        #
        sidebar = dbc.Nav(
            [
                html.Div(
                    [
                        dbc.Nav(
                            [
                                dbc.NavItem(dbc.NavLink([html.Img(
                                    src=f'{config.get_config().application.icons_path}dashboard.png', className="feather"), " Dashboard"], href="#", active=True))
                            ],
                            className="flex-column"
                        )
                    ],
                    className="sidebar-sticky pt-3")
            ],
            className="col-md-3 col-lg-2 d-md-block sidebar collapse",
            vertical=True
        )

        #       -------------------------------------------------
        #       |                                               |
        #       |                                               |
        #       |         **************************************|
        #       |         **************************************|
        #       |         **************************************|
        #       |         **************************************|
        #       |         **************************************|
        #       |         **************************************|
        #       |         **************************************|
        #       |         **************************************|
        #       |         **************************************|
        #       -------------------------------------------------
        #
        main = html.Main(
            [
                charts_update_clock,
                html.Div(html.H2(
                    "Network"), className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"),
                network_chart.layout,
                html.Div(html.H2("Map"), id="geo",
                         className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"),
                map_chart.layout

            ],
            className="col-md-9 ml-sm-auto col-lg-10 px-md-4",
            role="main"
        )

        #       -------------------------------------------------
        #       |***********************************************|
        #       |***********************************************|
        #       |***********************************************|
        #       |***********************************************|
        #       |***********************************************|
        #       |***********************************************|
        #       |***********************************************|
        #       |***********************************************|
        #       |***********************************************|
        #       |***********************************************|
        #       |***********************************************|
        #       -------------------------------------------------
        #
        layout = html.Div(
            [
                navbar,
                html.Div(
                    [
                        html.Div(
                            [
                                sidebar,
                                main

                            ],
                            className="row"
                        )
                    ],
                    className="container-fluid"
                )
            ]
        )

        dash.layout = layout
        dash.title = config.get_config().application.title

        print("Application ready.")

    def go(self):
        """Start the application's thread"""
        self.start()
        self.running = True
        print("Application running.")

    def run(self):
        """Run the Dash application and process the incoming data"""
        Thread(daemon=True, target=dash.run_server, args=(
            config.get_config().application.host,
            config.get_config().application.port,
            False)).start()
        while self.running or not self.queue.empty():
            data_type, data = self.queue.get()
            self.dispatch_analysed_data(data_type, data)
            self.queue.task_done()
        print("Application stoped.")

    def stop(self):
        """Stop the application and the data processing"""
        self.running = False

    def dispatch_analysed_data(self, data_type, data):
        """Send the new data to the corresponding charts"""
        if data_type == "endpoint":
            network_chart.add_node(data)
            map_chart.add_point(data)

        elif data_type == "conversation":
            network_chart.add_edge(data)

##########################################################################
#                        C  A  L  L  B  A  C  K  S                       #
##########################################################################


@dash.callback([Output('network', 'elements'),
                Output('geolocation', 'data')], Input('charts_update_clock', 'n_intervals'))
def charts_update(n_intervals):
    """Refresh the charts"""
    return network_chart.get_data(), map_chart.get_data()


@dash.callback([Output("map_info", "header"),
                Output("map_info", "children")], [Input("geolocation", "hover_feature")])
def geolocation_hover(feature):
    """Display additional information about map pins"""
    if feature:
        data = feature["properties"]["data"]
        title = ""
        info = []
        if "ip_addr" in data.keys():
            title = f'Adresse IPv{data["network_address_version"]}: {data["ip_addr"]}'

        for name, key in [("Nom d'hôte", "hostname"),
                          ("Continent", "continent_name"),
                          ("Pays", "country_name"),
                          ("Ville", "city_name")]:
            if key in data.keys():
                info += [f'{name}: {data[key]}', html.Br()]

        info = (html.P(info,
                       className="mb-0",
                       style={"padding": ".75rem"}))
        return title, info
    else:
        return "Survole un point pour obtenir des informations", [""]
