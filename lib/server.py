# -*- coding: utf-8 -*-

from . import config
from . import sniffer
from . import analyser
from . import application
from queue import Queue


class Server():

    sniffer = None
    analyser = None
    application = None
    running = None

    def __init__(self):
        """Initialize the server"""
        pakets_queue = Queue()
        data_queue = Queue()
        self.sniffer = sniffer.Sniffer(pakets_queue)
        self.analyser = analyser.Analyser(pakets_queue, data_queue)
        self.application = application.Application(data_queue)
        self.running = False
        print("Server ready.")

    def start(self):
        """Run the application with all the modules needed"""
        self.running = True
        self.sniffer.sniff(config.get_config().module.tshark.interface)
        self.analyser.analyse()
        self.application.go()
        print("Server running.")
        while self.running:
            try:
                input("")
            except:
                self.stop()
                break
        self.sniffer.stop()
        self.analyser.stop()
        self.analyser.join(timeout=15)
        print("Server stoped.")

    def stop(self):
        """Stop the server and its modules"""
        self.running = False
