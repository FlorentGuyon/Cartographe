# -*- coding: utf-8 -*-

from . import config
from threading import Thread
from queue import Queue
import geoip2.database


class Analyser(Thread):

    endpoints = None
    conversations = None
    sniffers_queue = None
    application_queue = None
    running = None

    def __init__(self, sniffers_queue, application_queue):
        """Initialize an packet analyser"""
        Thread.__init__(self, daemon=True)
        self.sniffers_queue = sniffers_queue
        self.application_queue = application_queue
        self.endpoints = {}
        self.conversations = {}
        self.running = False
        print("Analyser ready.")

    def analyse(self):
        """Start the packet analyse"""
        self.running = True
        self.start()
        print("Analyser running.")

    def run(self):
        """Get the packet sniffed and extract the data"""
        while self.running or not self.sniffers_queue.empty():
            packet = self.sniffers_queue.get()
            self.extract_data(packet)
            self.sniffers_queue.task_done()
        print("Analyser stoped.")

    def stop(self):
        """Stop analyzing the packets"""
        self.running = False

    def extract_data(self, packet):
        """Extract all the data from the packet and the databases"""

        src, dst = {}, {}

        for (index, value) in [
                ("ip_addr", "ip.src"),
                ("hostname", "ip.src_host")]:
            try:
                src[index] = packet["_source"]["layers"]["ip"][value]
            except:
                src[index] = None

        for (index, value) in [
                ("ip_addr", "ip.dst"),
                ("hostname", "ip.dst_host")]:
            try:
                dst[index] = packet["_source"]["layers"]["ip"][value]
            except:
                dst[index] = None

        for data in (src, dst):
            if data["ip_addr"] and data["ip_addr"] not in self.endpoints.keys():
                data.update(self.get_ip_info(data["ip_addr"]))
                self.endpoints[data["ip_addr"]] = data
                self.application_queue.put(("endpoint", data))

        if src["ip_addr"] and dst["ip_addr"] and (src["ip_addr"], dst["ip_addr"]) not in self.conversations.keys():
            data = {
                "ip_src": src["ip_addr"],
                "ip_dst": dst["ip_addr"]
            }
            self.conversations[(src["ip_addr"], dst["ip_addr"])] = data
            self.application_queue.put(("conversation", data))

    def get_ip_info(self, ip):
        """Search for data through a free GeoIP2 database"""

        # Example : {'city_confidence': None, 'city_name': 'Dublin', 'continent_code': 'EU', 'continent_name': 'Europe', 'country_confidence': None, 'is_country_in_european_union': True, 'country_code': 'IE', 'country_name': 'Ireland', 'local_average_income': None, 'coordinates_accuracy_radius': 1000, 'latitude': 53.3331, 'longitude': -6.2489, 'metro_code': None, 'population_density': None, 'time_zone': 'Europe/Dublin', 'postal_code': 'D02', 'registered_country_confidence': None, 'is_registered_country_in_european_union': False, 'registered_country_code': 'US', 'registered_country_name': 'United States', 'represented_country_confidence': None, 'is_represented_country_in_european_union': False, 'represented_country_code': None, 'represented_country_name': None, 'represented_country_type': None, 'subdivisions': [{'subdivision_confidence': None, 'subdivision_code': 'L', 'subdivision_name': 'Leinster'}], 'as': None, 'connection_type': None, 'domain': None, 'is_anonymous': False, 'is_anonymous_proxy': False, 'is_anonymous_vpn': False, 'is_hosting_provider': False, 'is_legitimate_proxy': False, 'is_public_proxy': False, 'is_satellite_provider': False, 'is_tor_exit_node': False, 'isp': None, 'organization': None, 'static_ip_score': None, 'user_count': None, 'user_type': None, 'is_multicast': False, 'is_private': False, 'is_unspecified': False, 'is_reserved': False, 'is_loopback': False, 'is_link_local': False, 'with_prefixlen': IPv4Network('52.48.0.0/14'), 'compressed': '52.48.0.0/14', 'exploded': '52.48.0.0/14', 'with_netmask': '52.48.0.0/255.252.0.0', 'with_hostmask': '52.48.0.0/0.3.255.255', 'num_addresses': 262144, 'prefixlen': 14, 'network_address_version': 4, 'network_address_max_prefixlen': 32, 'network_address_compressed': '52.48.0.0', 'network_address_exploded': '52.48.0.0', 'network_address_reverse_pointer': '0.0.48.52.in-addr.arpa', 'network_address_is_multicast': False, 'network_address_is_private': False, 'network_address_is_global': True, 'network_address_is_unspecified': False, 'network_address_is_reserved': False, 'network_address_is_loopback': False, 'network_address_is_link_local': False, 'broadcast_address_version': 4, 'broadcast_address_max_prefixlen': 32, 'broadcast_address_compressed': '52.51.255.255', 'broadcast_address_exploded': '52.51.255.255', 'broadcast_address_reverse_pointer': '255.255.51.52.in-addr.arpa', 'broadcast_address_is_multicast': False, 'broadcast_address_is_private': False, 'broadcast_address_is_global': True, 'broadcast_address_is_unspecified': False, 'broadcast_address_is_reserved': False, 'broadcast_address_is_loopback': False, 'broadcast_address_is_link_local': False, 'hostmask_version': 4, 'hostmask_max_prefixlen': 32, 'hostmask_compressed': '0.3.255.255', 'hostmask_exploded': '0.3.255.255', 'hostmask_reverse_pointer': '255.255.3.0.in-addr.arpa', 'hostmask_is_multicast': False, 'hostmask_is_private': True, 'hostmask_is_global': False, 'hostmask_is_unspecified': False, 'hostmask_is_reserved': False, 'hostmask_is_loopback': False, 'hostmask_is_link_local': False, 'netmask_version': 4, 'netmask_max_prefixlen': 32, 'netmask_compressed': '255.252.0.0', 'netmask_exploded': '255.252.0.0', 'netmask_reverse_pointer': '0.0.252.255.in-addr.arpa', 'netmask_is_multicast': False, 'netmask_is_private': True, 'netmask_is_global': False, 'netmask_is_unspecified': False, 'netmask_is_reserved': True, 'netmask_is_loopback': False, 'netmask_is_link_local': False}
        data = {}

        with geoip2.database.Reader(config.get_config().database.geolite2_city.path) as database:
            try:
                geoip2_city = database.city(ip)

                geoip2_records_city = geoip2_city.city
                data["city_confidence"] = geoip2_records_city.confidence
                data["city_name"] = geoip2_records_city.name

                geoip2_records_continent = geoip2_city.continent
                data["continent_code"] = geoip2_records_continent.code
                data["continent_name"] = geoip2_records_continent.name

                geoip2_records_country = geoip2_city.country
                data["country_confidence"] = geoip2_records_country.confidence
                data["is_country_in_european_union"] = geoip2_records_country.is_in_european_union
                data["country_code"] = geoip2_records_country.iso_code
                data["country_name"] = geoip2_records_country.name

                geoip2_records_location = geoip2_city.location
                data["local_average_income"] = geoip2_records_location.average_income
                data["coordinates_accuracy_radius"] = geoip2_records_location.accuracy_radius
                data["latitude"] = geoip2_records_location.latitude
                data["longitude"] = geoip2_records_location.longitude
                data["metro_code"] = geoip2_records_location.metro_code
                data["population_density"] = geoip2_records_location.population_density
                data["time_zone"] = geoip2_records_location.time_zone

                geoip2_records_postal = geoip2_city.postal
                data["postal_code"] = geoip2_records_postal.code

                geoip2_records_registered_country = geoip2_city.registered_country
                data["registered_country_confidence"] = geoip2_records_registered_country.confidence
                data["is_registered_country_in_european_union"] = geoip2_records_registered_country.is_in_european_union
                data["registered_country_code"] = geoip2_records_registered_country.iso_code
                data["registered_country_name"] = geoip2_records_registered_country.name

                geoip2_records_represented_country = geoip2_city.represented_country
                data["represented_country_confidence"] = geoip2_records_represented_country.confidence
                data["is_represented_country_in_european_union"] = geoip2_records_represented_country.is_in_european_union
                data["represented_country_code"] = geoip2_records_represented_country.iso_code
                data["represented_country_name"] = geoip2_records_represented_country.name
                data["represented_country_type"] = geoip2_records_represented_country.type

                data["subdivisions"] = []
                for geoip2_records_subdivision in geoip2_city.subdivisions:
                    data["subdivisions"].append({
                        "subdivision_confidence": geoip2_records_subdivision.confidence,
                        "subdivision_code": geoip2_records_subdivision.iso_code,
                        "subdivision_name": geoip2_records_subdivision.name})

                geoip2_records_traits = geoip2_city.traits
                data["as"] = geoip2_records_traits.autonomous_system_organization
                data["connection_type"] = geoip2_records_traits.connection_type
                data["domain"] = geoip2_records_traits.domain
                data["is_anonymous"] = geoip2_records_traits.is_anonymous
                data["is_anonymous_proxy"] = geoip2_records_traits.is_anonymous_proxy
                data["is_anonymous_vpn"] = geoip2_records_traits.is_anonymous_vpn
                data["is_hosting_provider"] = geoip2_records_traits.is_hosting_provider
                data["is_legitimate_proxy"] = geoip2_records_traits.is_legitimate_proxy
                data["is_public_proxy"] = geoip2_records_traits.is_public_proxy
                data["is_satellite_provider"] = geoip2_records_traits.is_satellite_provider
                data["is_tor_exit_node"] = geoip2_records_traits.is_tor_exit_node
                data["isp"] = geoip2_records_traits.isp
                data["organization"] = geoip2_records_traits.organization
                data["static_ip_score"] = geoip2_records_traits.static_ip_score
                data["user_count"] = geoip2_records_traits.user_count
                data["user_type"] = geoip2_records_traits.user_type

                ipaddress = geoip2_records_traits.network
                data["is_multicast"] = ipaddress.is_multicast
                data["is_private"] = ipaddress.is_private
                data["is_unspecified"] = ipaddress.is_unspecified
                data["is_reserved"] = ipaddress.is_reserved
                data["is_loopback"] = ipaddress.is_loopback
                data["is_link_local"] = ipaddress.is_link_local
                data["with_prefixlen"] = ipaddress.with_prefixlen
                data["compressed"] = ipaddress.compressed
                data["exploded"] = ipaddress.exploded
                data["with_netmask"] = ipaddress.with_netmask
                data["with_hostmask"] = ipaddress.with_hostmask
                data["num_addresses"] = ipaddress.num_addresses
                data["prefixlen"] = ipaddress.prefixlen

                for (name, address) in [
                        ("network_address", ipaddress.network_address),
                        ("broadcast_address", ipaddress.broadcast_address),
                        ("hostmask", ipaddress.hostmask),
                        ("netmask", ipaddress.netmask)]:
                    data[f"{name}_version"] = address.version
                    data[f"{name}_max_prefixlen"] = address.max_prefixlen
                    data[f"{name}_version"] = address.version
                    data[f"{name}_compressed"] = address.compressed
                    data[f"{name}_exploded"] = address.exploded
                    data[f"{name}_reverse_pointer"] = address.reverse_pointer
                    data[f"{name}_is_multicast"] = address.is_multicast
                    data[f"{name}_is_private"] = address.is_private
                    data[f"{name}_is_global"] = address.is_global
                    data[f"{name}_is_unspecified"] = address.is_unspecified
                    data[f"{name}_is_reserved"] = address.is_reserved
                    data[f"{name}_is_loopback"] = address.is_loopback
                    data[f"{name}_is_link_local"] = address.is_link_local

            except:
                pass

        return data
