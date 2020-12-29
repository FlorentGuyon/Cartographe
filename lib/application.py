# -*- coding: utf-8 -*-

from os import listdir, remove, path
from psutil import sensors_battery, Process, virtual_memory, cpu_percent, disk_usage, net_io_counters, net_if_stats, net_if_addrs, AF_LINK
from socket import AF_INET
from datetime import timedelta, datetime
from json import loads, dumps
from pathlib import Path

from plotly.graph_objects import Figure, Indicator
from dash import Dash, callback_context, no_update
from dash.dependencies import Output, Input, State
from dash_html_components import Main, Div, Span, P, H2, Table, A, Br, Img
from dash_bootstrap_components import Nav, NavLink, NavItem, Navbar, NavbarBrand, NavbarToggler, Toast
from dash_core_components import Interval, Graph, Location
from dash_cytoscape import Cytoscape, load_extra_layouts
from dash_leaflet import GeoJSON, Map, TileLayer
from dash_leaflet.express import geojson_to_geobuf, dicts_to_geojson
from dash_extensions.javascript import arrow_function
from dash_table import DataTable
from dash.exceptions import PreventUpdate
from threading import Thread

from . import config
from . import logger

config.load_config()

##########################################################################
#                           C  L  A  S  S  E  S                          #
##########################################################################


class NetworkChart():

    layout = None
    classes = None
    last_update = None

    def __init__(self):
        """Create an empty network graph"""
        self.classes = []
        # Load the extended set of network layouts
        load_extra_layouts()

        # concentric, cose-bilkent, circle, dagre, breadthfirst, klay, cola, spread
        network_layout = config.get("user_network_layout")

        if network_layout is None:
            network_layout = config.get("default_network_layout")

            if network_layout is None:
                network_layout = "cose-bilkent"

        # https://js.cytoscape.org/
        self.layout = Cytoscape(
            id="network",
            layout={
                # https://js.cytoscape.org/#demos
                'name': network_layout,
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

        for file in listdir(f'{config.get("prog_path")}/assets/img/network_chart_icons/'):
            file_name = file.split('.')[0]
            self.classes.append(file_name)
            selector = {'selector': f'.{file_name}', 'style': {'background-image': f'/assets/img/network_chart_icons/{file}',
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
        self.add_element(node)

    def add_edge(self, data):
        """Add an edge between two nodes"""
        edge = {'data': {'source': data["ip_src"],
                         'target': data["ip_dst"],
                         'weight': None},
                'classes': None}
        self.add_element(edge)

    def add_compound(self, data):
        """Not used yet"""
        node = {'data': {'id': None, 'label': None,
                         'parent': None, 'color': None}, 'classes': None}
        self.add_element(compound)

    def add_element(self, element):
        self.layout.elements.append(element)
        self.last_update = datetime.now().timestamp()

    def get_data(self):
        return self.layout.elements


class MapChart():

    layout = None
    points = None

    def __init__(self):
        """Create an empty world map"""
        self.points = []

        map_info = Toast(
            [P("This is the content of the toast", className="mb-0")],
            header="This is the header",
            id="map_info",
            style={"z-index": "1000", "right": 0, "margin": "10px", "position": "absolute",
                   "background-color": "#262629", "opacity": 0.9, "border": "1px solid #555", "color": "#dbd6d6"}
        )

        # https://dash-leaflet.herokuapp.com/#choropleth_us
        # https://leafletjs.com/reference-1.3.4.html#geojson
        countries = GeoJSON(
            url='/assets/leaflet/countries.json',
            options=dict(
                style=dict(
                    opacity=0, 
                    fillOpacity=0)),
            zoomToBoundsOnClick=True,
            hoverStyle=arrow_function(dict(
                opacity=1, 
                color='#666666', 
                dashArray='',
                fillOpacity=0.25, 
                weight=1))
        )

        # https://dash-leaflet.herokuapp.com/
        self.layout = Map([
            TileLayer(
                url='https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png',
                minZoom=2,
                maxZoom=25,
                attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '
            ),
            # dl.LocateControl(startDirectly=True, options={'locateOptions': {'enableHighAccuracy': True}}),
            countries,
            GeoJSON(
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
        return geojson_to_geobuf(dicts_to_geojson(self.points))


class CaptureTable():

    data = None
    layout = None

    def __init__(self):
        self.data = self.get_captures()
        self.layout = DataTable(
            id='capture_table',
            data=self.data,
            sort_action='custom',
            row_deletable=True,
            columns=[{"id": i, "name": name} for (i, name) in [
                ("capture_start", "Start"),
                ("capture_end", "End"),
                ("capture_duration", "Duration"),
                ("capture_interface", "Interface"),
                ("capture_size", "Size")]])

    def get_captures(self):
        """Return the details of the captures files"""
        captures = []
        files = sorted(Path(f'{config.get("prog_path")}/capture/').glob('*.pcap'), reverse=True)

        for file in files:
            start, end, interface = file.name.replace(
                ".pcap", '').split('_')
            start = datetime.fromtimestamp(int(start))
            if end == "":
                now = datetime.now().timestamp()
                now = datetime.fromtimestamp(int(now))
                duration = (now - start).total_seconds()
                duration = seconds2delay(duration)
                end = "In progress..."
            else:
                end = datetime.fromtimestamp(int(end))
                duration = (end - start).total_seconds()
                duration = seconds2delay(duration)
                end = end.strftime("%d/%m/%Y %H:%M:%S")
            captures.append({
                "capture_start": start.strftime("%d/%m/%Y %H:%M:%S"),
                "capture_end": end,
                "capture_duration": duration,
                "capture_interface": interface,
                "capture_size": bytes2human(file.stat().st_size),
                "capture_file": f'{config.get("prog_path")}/capture/{file.name}'})

        return captures


class InterfaceTable():

    data = None
    layout = None

    def __init__(self):
        self.data = self.get_interfaces()
        self.layout = self.get_layout()

    def new_interface_object(self, name, state, speed, MAC, IPv4, sent, received):
        interface_object = {
            "interface_name": name,
            "interface_state": state,
            "interface_speed": speed,
            "interface_mac": MAC,
            "interface_ip": IPv4,
            "interface_sent": sent,
            "interface_received": received
        }
        return interface_object

    def get_interfaces(self):
        interfaces = []
        stats = net_io_counters(True)
        addresses = net_if_addrs()
        states = net_if_stats()
        for name in addresses:
            state = "Up" if states[name].isup else "Down"
            speed = states[name].speed * 1000
            speed = bytes2human(speed)
            MAC = [details.address for details in addresses[name]
                   if details.family is AF_LINK]
            MAC = MAC[0] if len(MAC) > 0 else ""
            IPv4 = [details.address for details in addresses[name]
                    if details.family is AF_INET]
            IPv4 = IPv4[0] if len(IPv4) > 0 else ""
            sent = stats[name].bytes_sent
            sent = bytes2human(sent)
            received = stats[name].bytes_recv
            received = bytes2human(received)
            interfaces.append(self.new_interface_object(
                name, state, speed, MAC, IPv4, sent, received))
        interfaces = sorted(
            interfaces, key=lambda interface: interface["interface_state"], reverse=True)

        return interfaces

    def get_layout(self):
        layout = DataTable(
            id='interface_table',
            data=self.data,
            sort_action='custom',
            style_data_conditional=[
                {"if": {"filter_query": "{interface_state} = 'Down'"}, "opacity": "0.25"}],
            style_cell_conditional=[
                {"if": {"column_id": "interface_name"}, "width": "20%"},
                {"if": {"column_id": "interface_state"}, "width": "10%"},
                {"if": {"column_id": "interface_speed"}, "width": "10%"},
                {"if": {"column_id": "interface_mac"}, "width": "20%"},
                {"if": {"column_id": "interface_ip"}, "width": "20%"},
                {"if": {"column_id": "interface_received"}, "width": "10%"},
                {"if": {"column_id": "interface_sent"}, "width": "10%"}],
            columns=[{"id": id_, "name": name} for (id_, name) in [
                ("interface_name", "Name"),
                ("interface_state", "State"),
                ("interface_speed", "Speed"),
                ("interface_mac", "MAC"),
                ("interface_ip", "IPv4"),
                ("interface_sent", "Sent"),
                ("interface_received", "Received")]])

        return layout


class LogTable():
    """Create a table with the log of all the log files of the program"""
    data = None
    layout = None
    dir_ = None
    file_format = None
    default_colors = None
    colors = None
    levels = None

    def __init__(self):
        """Initialize the layout of the table with its data"""
        self.dir_ = f'{config.get("prog_path")}/log/'
        self.file_format = "log"
        self.default_colors = config.get("default_colors_by_log_level")
        self.colors = self.default_colors
        self.levels = ["Debug", "Info", "Warning", "Error", "Critical"]
        self.data = self.get_logs()
        self.layout = self.get_layout()

    def new_log_object(self, date, level, message):
        """Create an object countaining all the needed inforamtion"""
        log_object = {
            "log_date": date.strftime("%d/%m/%Y %H:%M:%S"),
            "log_level": level.title(),
            "log_message": message
        }
        return log_object

    def get_files(self):
        """List all the log files of the program"""
        files = []
        if (self.dir_ is None) or (self.file_format is None):
            logger.log.error(
                "The log files cannot be found because the configuration is not valid.")
        else:
            files = sorted(Path(self.dir_).glob(f'*.{self.file_format}'))
        return files

    def get_logs(self):
        """Get the list of custom log objects"""
        logs = []
        files = self.get_files()

        for file in files:
            with open(file, 'r') as content:
                for line in content:
                    date, level, message = line.strip().split('    ')
                    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S,%f")
                    logs.insert(0, self.new_log_object(date, level, message))
        return logs

    def get_layout(self):
        """Get the HTML layout of the table"""
        style_data = []

        if (self.levels is None) or (self.colors is None) or (len(self.levels) != len(self.colors)):
            logger.log.error(
                "The log file table cannot be colored because the configuration is not valid.")
        else:
            style_data = [{"if": {"filter_query": "{log_level} = '" + level + "'"}, "color": color}
                          for level, color in zip(self.levels, self.colors)]

        layout = DataTable(
            id='log_table',
            data=self.data,
            sort_action='custom',
            style_data_conditional=style_data,
            style_cell_conditional=[
                {"if": {"column_id": "log_date"}, "width": "20%"},
                {"if": {"column_id": "log_level"}, "width": "20%"}],
            columns=[{"id": id_, "name": name} for (id_, name) in [
                ("log_date", "Date"),
                ("log_level", "Level"),
                ("log_message", "Message")]],
            style_cell={
                "whiteSpace": "normal"})

        return layout


class LogFileTable():
    """Create a table with some information about the log files of the program"""

    data = None
    layout = None
    dir_ = None
    file_format = None
    default_colors = None
    colors = None
    levels = None

    def __init__(self):
        """Initialize the layout of the table with its data"""
        self.dir_ = f'{config.get("prog_path")}/log/'
        self.file_format = "log"
        self.default_colors = config.get("default_colors_by_log_level")
        self.colors = self.default_colors
        self.levels = ["Debug", "Info", "Warning", "Error", "Critical"]
        self.data = self.get_files_data()
        self.layout = self.get_layout()

    def new_log_file_object(self, id_, date, debug_count, info_count, warning_count, error_count, critical_count, size, path):
        """Create a custom log file object with all the needed information"""
        log_file_object = {
            "log_file_id": id_,
            "log_file_date": date,
            "log_file_debug": debug_count,
            "log_file_info": info_count,
            "log_file_warning": warning_count,
            "log_file_error": error_count,
            "log_file_critical": critical_count,
            "log_file_size": size,
            "log_file_path": path
        }
        return log_file_object

    def get_files(self):
        """Get all the log files of the program"""
        files = []
        if (self.dir_ is None) or (self.file_format is None):
            logger.log.error(
                "The log files cannot be found because the configuration is not valid.")
        else:
            files = sorted(Path(self.dir_).glob(f'*.{self.file_format}'))
        return files

    def get_files_data(self):
        """Get the list of custom log file object"""
        log_files = []
        files = self.get_files()
        id_ = 1
        for file in files:
            if "__" in file.name:
                date, stats = file.name.split('.')[0].split('__')
                date = date.replace("-", "/")
                debug_count, info_count, warning_count, error_count, critical_count = stats.split(
                    '_')
                size = bytes2human(file.stat().st_size)
                path = str(file)
                log_files.insert(0, self.new_log_file_object(
                    id_, date, debug_count, info_count, warning_count, error_count, critical_count, size, path))
                id_ += 1
        return log_files

    def get_layout(self):
        """Get the HTML layout of the table"""
        style_data = []

        if (self.levels is None) or (self.colors is None) or (len(self.levels) != len(self.colors)):
            logger.log.error(
                "The log file table cannot be colored because the configuration is not valid.")
        else:
            style_data = [{"if": {"column_id": f'log_file_{level.lower()}'}, "color": color} for level, color in zip(self.levels, self.colors)]

        layout = DataTable(
            id='log_file_table',
            data=self.data,
            row_deletable=True,
            sort_action='custom',
            style_data_conditional=style_data,
            style_cell_conditional=[
                {"if": {"column_id": "log_file_id"}, "width": "10%"},
                {"if": {"column_id": "log_file_date"}, "width": "20%"},
                {"if": {"column_id": "log_file_debug"}, "width": "10%"},
                {"if": {"column_id": "log_file_info"}, "width": "10%"},
                {"if": {"column_id": "log_file_warning"}, "width": "10%"},
                {"if": {"column_id": "log_file_error"}, "width": "10%"},
                {"if": {"column_id": "log_file_critical"}, "width": "10%"},
                {"if": {"column_id": "log_file_size"}, "width": "20%"}],
            columns=[{"id": id_, "name": name} for (id_, name) in [
                ("log_file_id", "#"),
                ("log_file_date", "Date"),
                ("log_file_debug", "Debug"),
                ("log_file_info", "Info"),
                ("log_file_warning", "Warning"),
                ("log_file_error", "Error"),
                ("log_file_critical", "Critical"),
                ("log_file_size", "Size")]])

        return layout


class VitalsGrid():
    """Create a grid with some stats about the system"""
    data = None
    layout = None
    updating = None

    def __init__(self):
        self.updating = False
        self.data = self.get_data()
        self.layout = self.get_layout()

    def get_layout(self):
        """Get the HTML layout of the grid"""
        layout = Div([
            Div([
                Div(Graph(id="battery_status",
                          figure=self.data[0]),
                    className="col-12 col-lg-6"),
                Div(Graph(id="ram_status",
                          figure=self.data[1]),
                    className="col-12 col-lg-6"),
                Div(Graph(id="cpu_status",
                          figure=self.data[2]),
                    className="col-12 col-lg-6"),
                Div(Graph(id="disk_status",
                          figure=self.data[3]),
                    className="col-12 col-lg-6")],
                className="row")],
            className="container-fluid")

        return layout

    def make_new_indicator(self, title="", subtitle="", value=0, red=False):
        """Create a custom indicator object with all the needed information"""
        new_indicator = Figure(
            Indicator(
                title=f'{title}<br><span style="font-size: 0.8em; color: gray">{subtitle}</span>',
                mode="number",
                value=value,
                number={'suffix': "%", 'font': {
                    'color': ("#bd1212" if red else "#dbd6d6")}},
            ),
            layout={
                "paper_bgcolor": "#181a1b",
                "font": {'color': "#dbd6d6"}
            }
        )
        return new_indicator

    def pretty_percent(self, percent):

        if percent >= 1.0:
            return int(percent)

        if percent == 0.0:
            return 0

        float_ = f'{percent:.100f}'
        without_zeros = float_.replace('0', '')
        first_int = without_zeros[1]
        first_int_index = float_.find(first_int)
        decimal_count = first_int_index - 1
        pretty_percent = f'{percent:.{decimal_count}f}'

        return pretty_percent

    def get_data(self):
        """Get the list of custom indicator objects"""
        self.updating = True
        data = []

        # RAM
        # https://psutil.readthedocs.io/en/latest/#processes
        battery = sensors_battery()
        subtitle = 'Plugged' if battery.power_plugged else 'Unplugged'
        # Right after unpluging, the battery life time is false (too long)
        if not battery.power_plugged and battery.secsleft < (24 * 60 * 60):
            subtitle += f', {timedelta(seconds=battery.secsleft)} left'
        critic = (not battery.power_plugged and battery.percent < 20)
        data.append(self.make_new_indicator(
            "Battery", subtitle, battery.percent, critic))

        # RAM
        current_process = Process()
        app_ram_usage = bytes2human(current_process.memory_info().rss)
        app_ram_percent = float(current_process.memory_percent())
        app_ram_percent = self.pretty_percent(app_ram_percent)
        subtitle = f'Cartographe: {app_ram_usage} ({app_ram_percent}%)'
        ram_percent = int(virtual_memory().percent)
        critic = (ram_percent > 90)
        data.append(self.make_new_indicator(
            "RAM", subtitle, ram_percent, critic))

        # CPU
        app_cpu_usage = float(current_process.cpu_percent(interval=None))
        app_cpu_usage = self.pretty_percent(app_cpu_usage)
        subtitle = f'Cartographe: {app_cpu_usage}%'
        cpu_usage = int(cpu_percent(interval=None))
        cpu_critic = (cpu_usage > 90)
        data.append(self.make_new_indicator(
            "CPU", subtitle, cpu_usage, cpu_critic))

        # Disk
        disk = disk_usage(str(Path(__file__).parent.absolute()))
        app_disk_used = sum(f.stat().st_size
                            for f in Path(config.get("prog_path")).glob('**/*') if f.is_file())
        app_disk_percent = float(app_disk_used * 100 / disk.total)
        app_disk_percent = self.pretty_percent(app_disk_percent)
        app_disk_used = bytes2human(app_disk_used)
        subtitle = f'Cartographe: {app_disk_used} ({app_disk_percent}%)'
        disk_percent = int(disk.percent)
        critic = (disk_percent > 90)
        data.append(self.make_new_indicator(
            "Disk", subtitle, disk_percent, critic))

        self.updating = False

        return data


##########################################################################
#                        F  U  N  C  T  I  O  N  S                       #
##########################################################################


def bytes2human(n, decimals=0):
    """Convert the size (in Bytes) with the corresponding symbol: 1024 -> 1K"""
    # http://code.activestate.com/recipes/578019
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return f'%.{decimals}f%s' % (value, s)
    return "%sB" % n


def seconds2delay(seconds):
    """Return a human readable delay"""
    years, seconds = divmod(seconds, 365 * 24 * 60 * 60)
    mounts, seconds = divmod(seconds, 31 * 24 * 60 * 60)
    days, seconds = divmod(seconds, 24 * 60 * 60)
    hours, seconds = divmod(seconds, 60 * 60)
    minutes, seconds = divmod(seconds, 60)

    delay = ""

    if int(years) > 0:
        delay += f'{int(years)}y '
    if int(mounts) > 0:
        delay += f'{int(mounts)}m '
    if int(days) > 0:
        delay += f'{int(days)}d '
    if int(hours) > 0:
        delay += f'{int(hours)}h '
    if int(minutes) > 0:
        delay += f'{int(minutes)}m '
    if int(seconds) > 0:
        delay += f'{int(seconds)}s'

    return delay


##########################################################################
#                       V  A  R  I  A  B  L  E  S                        #
##########################################################################

mydash = Dash(update_title=None)
# https://dash.plotly.com/callback-gotchas
mydash.config.suppress_callback_exceptions = True
mydash.title = "Cartographe"
layouts = {}
current_layout = "dashboard"
network_chart = NetworkChart()
map_chart = MapChart()
capture_list = CaptureTable()
log_list = LogTable()
log_file_list = LogFileTable()
interface_list = InterfaceTable()
vitals_grid = VitalsGrid()

##########################################################################
#                            L  A  Y  O  U  T                            #
##########################################################################

############################ N  A  V  B  A  R ############################
#
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
navbar = Navbar(
    [
        A(
            [
                Span(Img(src='/assets/img/icon.png',
                         width=30, className="logo"),
                     className="mr-2"),
                NavbarBrand("Cartographe",
                            className="ml-2")
            ],
            href=f'/{"dashboard"}'
        ),
        NavbarToggler(id="navbar-toggler"),
    ],
    className="navbar sticky-top flex-md-nowrap shadow",
    color="#212325",
    dark=True,
)
########################## S  I  D  E  B  A  R ##########################
#
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
sidebar = Nav([
    Div([
        Nav(
            children=[
                NavItem([
                    NavLink([Img(src='/assets/img/dashboard.svg',
                                 className="feather"), " Dashboard"],
                            id="navlink_dashboard",
                            href="/dashboard",
                            className=""),
                    Span([],
                         id="dashboard_badge",
                         className="badge")]),
                NavItem([
                    NavLink([Img(src='/assets/img/vitals.svg',
                                 className="feather"), " Vitals"],
                            id="navlink_vitals",
                            href="/vitals",
                            className=""),
                    Span([],
                         id="vitals_badge",
                         className="badge")]),
                NavItem([
                    NavLink([Img(src='/assets/img/captures.svg',
                                 className="feather"), " Captures"],
                            id="navlink_captures",
                            href="/captures",
                            className=""),
                    Span([],
                         id="captures_badge",
                         className="badge")]),
                NavItem([
                    NavLink([Img(src='/assets/img/logs.svg',
                                 className="feather"), " Logs"],
                            id="navlink_logs",
                            href="/logs",
                            className=""),
                    Span([],
                         id="logs_badge",
                         className="badge")])
            ],
            className="flex-column",
        )
    ],
        className="sidebar-sticky pt-3")
],
    className="col-md-3 col-lg-2 d-md-block sidebar collapse",
    vertical=True
)
############################# M  A  I  N ############################
#
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
###################### D  A  S  H  B  O  A  R  D #####################

interval = config.get("user_dashboard_update_interval")

if interval is None:
    interval = config.get("default_dashboard_update_interval")

    if interval is None:
        interval = 1000

dashboard_update_clock = Interval(
    id='dashboard_update_clock',
    interval=interval)

badge_update_clock = Interval(
    id='badge_update_clock',
    interval=interval)

layouts["dashboard"] = [
    dashboard_update_clock,
    Div(H2("Network"),
        className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"),
    network_chart.layout,
    Div(H2("Map"),
        id="geo",
        className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"),
    map_chart.layout
]

########################## V  I  T  A  L  S ##########################

interval = config.get("user_vitals_update_interval")

if interval is None:
    interval = config.get("default_vitals_update_interval")

    if interval is None:
        interval = 1000

vitals_update_clock = Interval(
    id='vitals_update_clock',
    interval=interval)

layouts["vitals"] = [
    vitals_update_clock,
    Div(H2("Vitals"),
        className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"),
    vitals_grid.layout
]

######################## C  A  P  T  U  R  E  S ########################

interval = config.get("user_captures_update_interval")

if interval is None:
    interval = config.get("default_captures_update_interval")

    if interval is None:
        interval = 1000

captures_update_clock = Interval(
    id='captures_update_clock',
    interval=interval)

layouts["captures"] = [
    captures_update_clock,
    Div(H2("Interfaces"),
        className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"),
    interface_list.layout,
    Div(children=[],
        id="interface_list_storage",
        style={"display": "none"}),
    Br(),
    Br(),
    Div(H2("Captures"),
        className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"),
    capture_list.layout,
    Div(children=[],
        id="capture_list_storage",
        style={"display": "none"})
]

############################## L  O  G  S  ##############################

interval = config.get("user_logs_update_interval")

if interval is None:
    interval = config.get("default_logs_update_interval")

    if interval is None:
        interval = 1000

logs_update_clock = Interval(
    id='logs_update_clock',
    interval=interval)

layouts["logs"] = [
    logs_update_clock,
    Div(H2("Archives"),
        className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"),
    log_file_list.layout,
    Div(children=[],
        id="log_file_list_storage",
        style={"display": "none"}),
    Br(),
    Br(),
    Div(H2("Logs"),
        className="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"),
    log_list.layout,
    Div(children=[],
        id="log_list_storage",
        style={"display": "none"})
]

############################## M  A  I  N ##############################

main = Main(
    children=[],
    id='main_section',
    className="col-md-9 ml-sm-auto col-lg-10 px-md-4",
    role="main"
)

############################ T  O  T  A  L ############################
#
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
layout = Div(
    [
        Location(id='url', refresh=False),
        badge_update_clock,
        navbar,
        Div(
            [
                Div(
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

mydash.layout = layout

##########################################################################
#                        C  A  L  L  B  A  C  K  S                       #
##########################################################################


@mydash.callback(Output('main_section', 'children'),
                 Output('navlink_dashboard', 'className'),
                 Output('navlink_vitals', 'className'),
                 Output('navlink_captures', 'className'),
                 Output('navlink_logs', 'className'),
                 Input('url', 'pathname'))
def display_page(pathname):
    """Send the current layout"""

    if pathname == "/":
        current = "dashboard"
    else:
        current = pathname[1:]

    output = []

    output.append(layouts[current])
    output.append(("active" if current == "dashboard" else ""))
    output.append(("active" if current == "vitals" else ""))
    output.append(("active" if current == "captures" else ""))
    output.append(("active" if current == "logs" else ""))

    return output


@mydash.callback(Output('vitals_badge', 'children'),
                 Output('logs_badge', 'children'),
                 Input('badge_update_clock', 'n_intervals'),
                 State('url', 'pathname'),
                 State('logs_badge', 'children'))
def update_badges(ignore, pathname, logs_badge):
    """Update the badge next to each link of the sidebar"""

    # VITALS
    if pathname[1:] == "vitals":
        vitals_badge = None
    else:
        vitals_badge = 0
        # Battery
        battery = sensors_battery()
        if (not battery.power_plugged) and (battery.percent < 20):
            vitals_badge += 1
        # CPU
        if int(cpu_percent(interval=None)) > 90:
            vitals_badge += 1
        # Disk
        disk = disk_usage(str(Path(__file__).parent.absolute()))
        if int(disk.percent) > 90:
            vitals_badge += 1
        # RAM
        if int(virtual_memory().percent) > 90:
            vitals_badge += 1

        if vitals_badge == 0:
            vitals_badge = None

    # LOGS
    if pathname[1:] == "logs":
        logs_badge = None

    else:
        if type(logs_badge) is list:
            if len(logs_badge) > 0:
                logs_badge = logs_badge[0]
            else:
                logs_badge = 0
        elif logs_badge is None:
            logs_badge = 0

        logs_badge += logger.log.get_recent_error_count()

        if logs_badge == 0:
            logs_badge = None

    return vitals_badge, logs_badge


@mydash.callback(Output('network', 'elements'),
                 Output('geolocation', 'data'),
                 Input('dashboard_update_clock', 'n_intervals'))
def dashboard_update(n_intervals):
    """Refresh the charts"""

    if network_chart.last_update is not None:

        last_update = int(
            (datetime.now().timestamp() - network_chart.last_update))
        interval = int(config.get("default_dashboard_update_interval"))

        if last_update >= (interval / 1000):
            return network_chart.get_data(), map_chart.get_data()

    raise PreventUpdate


@mydash.callback(Output('capture_list_storage', 'children'),
                 Output('interface_list_storage', 'children'),
                 Input('interface_table', 'data'),
                 Input('interface_table', 'sort_by'),
                 Input('capture_table', 'data'),
                 Input('capture_table', 'sort_by'),
                 Input('captures_update_clock', 'n_intervals'),
                 State('capture_table', 'data_previous'))
def prepare_capture_list(interfaces, interfaces_sort_by, current, captures_sort_by, ignore, previous):
    """Refresh the charts"""
    ctx = callback_context

    # No update
    if not ctx.triggered:
        raise PreventUpdate
    # Delete a capture
    elif ctx.triggered[0]["prop_id"] == "capture_table.data":
        if previous and current:
            for capture in previous:
                if capture not in current:
                    remove(capture["capture_file"])
        raise PreventUpdate

    # Update the capture list
    elif ctx.triggered[0]["prop_id"] == "captures_update_clock.n_intervals":
        current = capture_list.get_captures()
        interfaces = interface_list.get_interfaces()

    # Sort the captures
    if captures_sort_by:
        column, direction = captures_sort_by[0].values()
        if column == "capture_interface":
            current = sorted(current,
                             key=lambda capture: capture[column],
                             reverse=(direction == "desc"))
        elif column == "capture_size":
            current = sorted(current,
                             key=lambda capture: int(capture[column]
                                                     .replace('Y', "000Z")
                                                     .replace('Z', "000E")
                                                     .replace('E', "000P")
                                                     .replace('P', "000T")
                                                     .replace('T', "000G")
                                                     .replace('G', "000M")
                                                     .replace('M', "000K")
                                                     .replace('K', "000B")
                                                     .replace('B', "")),
                             reverse=(direction == "desc"))
        elif column == "capture_duration":
            current = sorted(current,
                             key=lambda capture: int(capture[column]
                                                     .replace('y', "0000000000")
                                                     .replace('m', "00000000")
                                                     .replace('d', "000000")
                                                     .replace('h', "0000")
                                                     .replace('m', "00")
                                                     .replace('s', '')
                                                     .replace(' ', '')),
                             reverse=(direction == "desc"))
        elif column in ["capture_start", "capture_end"]:
            current = sorted(current, key=lambda capture:
                             (datetime.strptime(capture[column], '%d/%m/%Y %H:%M:%S').timestamp() if capture[column] != "In progress..."
                              else datetime.now().timestamp()),
                             reverse=(direction == "desc"))

     # Sort the captures
    if interfaces_sort_by:
        column, direction = interfaces_sort_by[0].values()
        if column in ["interface_name", "interface_state", "interface_mac", "interface_ip"]:
            interfaces = sorted(interfaces,
                                key=lambda interface: interface[column],
                                reverse=(direction == "desc"))
        elif column in ["interface_speed", "interface_sent", "interface_received"]:
            interfaces = sorted(interfaces,
                                key=lambda interface: int(interface[column]
                                                          .replace('Y', "000Z")
                                                          .replace('Z', "000E")
                                                          .replace('E', "000P")
                                                          .replace('P', "000T")
                                                          .replace('T', "000G")
                                                          .replace('G', "000M")
                                                          .replace('M', "000K")
                                                          .replace('K', "000B")
                                                          .replace('B', "")),
                                reverse=(direction == "desc"))

    return dumps(current), dumps(interfaces)


@mydash.callback(Output('capture_table', 'data'),
                 Input('capture_list_storage', 'children'))
def update_capture_list(data):
    ctx = callback_context

    # No update
    if not ctx.triggered:
        raise PreventUpdate

    return loads(str(data))


@mydash.callback(Output('interface_table', 'data'),
                 Input('interface_list_storage', 'children'))
def update_interface_list(data):
    ctx = callback_context

    # No update
    if not ctx.triggered:
        raise PreventUpdate

    return loads(str(data))

##############################################################################


@mydash.callback(Output('log_list_storage', 'children'),
                 Output('log_file_list_storage', 'children'),
                 Input('log_table', 'data'),
                 Input('log_table', 'sort_by'),
                 Input('log_file_table', 'data'),
                 Input('log_file_table', 'sort_by'),
                 Input('logs_update_clock', 'n_intervals'),
                 State('log_file_table', 'data_previous'),
                 State('url', 'pathname'))
def prepare_log_list(logs, logs_sort_by, files, files_sort_by, ignore, previous_files, pathname):
    ctx = callback_context

    # No update
    if not ctx.triggered:
        raise PreventUpdate

    # Update the capture list
    if ctx.triggered[0]["prop_id"] == "logs_update_clock.n_intervals":
        logs = log_list.get_logs()

    # Update the capture list
    if ctx.triggered[0]["prop_id"] == "log_file_table.data":
        if previous_files and files:
            for previous_file in previous_files:
                if previous_file not in files:
                    file_path = previous_file["log_file_path"]
                    remove(file_path)
                    logger.log.info(f'Log file {file_path} have been deleted.')
                    if Path(file_path).is_file():
                        logger.log.warning(f'Log file {file_path} cannot be deleted.')
                    raise PreventUpdate

    files = log_file_list.get_files_data()

    if (files is not None) and (len(files) > 0):
        files[0]["log_file_debug"] = logger.log.debug_count
        files[0]["log_file_info"] = logger.log.info_count
        files[0]["log_file_warning"] = logger.log.warning_count
        files[0]["log_file_error"] = logger.log.error_count
        files[0]["log_file_critical"] = logger.log.critical_count

    # Sort the captures
    if logs_sort_by:
        column, direction = logs_sort_by[0].values()
        if column == "log_level":
            levels = ["Debug", "Info", "Warning", "Error", "Critical"]
            if levels is not None:
                logs = sorted(logs,
                              key=lambda log: levels.index(log[column]),
                              reverse=(direction == "desc"))
        elif column == "log_message":
            logs = sorted(logs,
                          key=lambda log: log[column],
                          reverse=(direction == "desc"))
        elif column == "log_date":
            logs = sorted(logs,
                          key=lambda log: datetime.strptime(
                              log[column], '%d/%m/%Y %H:%M:%S').timestamp(),
                          reverse=(direction == "desc"))

    # Sort the captures
    if files_sort_by:
        column, direction = files_sort_by[0].values()
        if column == "log_file_size":
            files = sorted(files,
                           key=lambda log_file: int(log_file[column]
                                                    .replace('Y', "000Z")
                                                    .replace('Z', "000E")
                                                    .replace('E', "000P")
                                                    .replace('P', "000T")
                                                    .replace('T', "000G")
                                                    .replace('G', "000M")
                                                    .replace('M', "000K")
                                                    .replace('K', "000")),
                           reverse=(direction == "desc"))
        elif column == "log_file_date":
            files = sorted(files,
                           key=lambda log_file: datetime.strptime(
                               log_file[column], '%d/%m/%Y').timestamp(),
                           reverse=(direction == "desc"))
        else:
            files = sorted(files,
                           reverse=(direction == "desc"))

    return dumps(logs), dumps(files)

###################


@mydash.callback(Output('log_table', 'data'),
                 Input('log_list_storage', 'children'))
def upate_log_list(data):
    ctx = callback_context

    # No update
    if not ctx.triggered:
        raise PreventUpdate

    return loads(str(data))


@mydash.callback(Output('log_file_table', 'data'),
                 Input('log_file_list_storage', 'children'))
def upate_log_file_list(data):
    ctx = callback_context

    # No update
    if not ctx.triggered:
        raise PreventUpdate

    return loads(str(data))

##############################################################################


@mydash.callback(Output('battery_status', 'figure'),
                 Output('ram_status', 'figure'),
                 Output('cpu_status', 'figure'),
                 Output('disk_status', 'figure'),
                 Input('vitals_update_clock', 'n_intervals'),
                 State('url', 'pathname'))
def vitals_update(n_intervals, pathname):
    """Refresh the charts"""
    ctx = callback_context

    # No update
    if not ctx.triggered:
        raise PreventUpdate

    if vitals_grid.updating:
        logger.log.warning(
            "The automatic update of the vitals page has been canceled because of a high latency from the previous update. Check the battery level and the RAM and CPU usage.")
        raise PreventUpdate

    data = vitals_grid.get_data()

    return data[0], data[1], data[2], data[3]

##############################################################################


@mydash.callback(Output("map_info", "header"),
                 Output("map_info", "children"),
                 Input("geolocation", "hover_feature"))
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
                info += [f'{name}: {data[key]}', Br()]

        info = (P(info,
                  className="mb-0",
                  style={"padding": ".75rem"}))
        return title, info
    else:
        return "Survole un point pour obtenir des informations", [""]


class Application(Thread):

    running = None

    def __init__(self, queue):
        """Generate a ready to run WEB server hosting a custom web site"""
        Thread.__init__(self, daemon=True)
        self.queue = queue
        self.running = False
        logger.log.info("Application ready.")

    def go(self):
        """Start the application's thread"""
        self.start()
        self.running = True

    def run(self):
        """Run the Dash application and process the incoming data"""
        host = config.get("server_host")
        if host == None:
            host = "127.0.0.1"

        port = config.get("server_port")
        if port == None:
            port = 80

        Thread(daemon=True, target=mydash.run_server,
               args=(host, port, False)).start()
        logger.log.info("Application running.")

        while self.running or not self.queue.empty():
            data_type, data = self.queue.get()
            self.dispatch_analysed_data(data_type, data)
            self.queue.task_done()
        logger.log.info("Application stoped.")

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
