# -*- coding: utf-8 -*-

import os
import signal
import json

from threading import Thread
from queue import Queue
from subprocess import Popen, PIPE

from . import config


class Sniffer(Thread):

    running = False
    queue = None

    def __init__(self, queue):
        """Initialize a Tshark based sniffer"""
        Thread.__init__(self)
        self.tshark_path = config.get_config().module.tshark.path
        self.queue = queue
        print("Sniffer ready.")

    def sniff(self, interface):
        """Start listening to a network interface"""
        self.interface = interface
        self.running = True
        self.start()

    def run(self):
        """Get the tshark data and send them to the analyser"""
        print("Sniffer running.")
        with Popen([self.tshark_path, "-i", self.interface, "-l", "-T", "json"], stdout=PIPE) as capture:
            packet = ""
            while self.running:
                line = capture.stdout.readline().decode()
                if line == "[\r\n":
                    pass
                elif line == "  },\r\n":
                    packet += '}'
                    packet = json.loads(packet)
                    self.queue.put(packet)
                    packet = ""
                else:
                    packet += line.strip()
            capture.terminate()
        print("Sniffer stoped.")

    def stop(self):
        """Stop sniffing"""
        self.running = False
