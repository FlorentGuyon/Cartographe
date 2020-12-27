# -*- coding: utf-8 -*-

from datetime import datetime
from queue import Queue

from . import logger
from . import config
from . import sniffer
from . import analyser
from . import application

config.load_config()


class Server():

    sniffer = None
    analyser = None
    application = None
    running = None

    def __init__(self):
        """Initialize the server"""
        pakets_queue = Queue()
        data_queue = Queue()
        self.sniffer = sniffer.Sniffer(pakets_queue, fix_files=True)
        self.analyser = analyser.Analyser(pakets_queue, data_queue)
        self.application = application.Application(data_queue)
        self.running = False
        logger.log.info("Server ready.")

    def start(self):
        """Run the application with all the modules needed"""
        interface = config.get("default_listening_interface")

        if interface is None:
            interface = "Wi-Fi"

        self.running = True
        self.sniffer.sniff(interface)
        self.analyser.analyse()
        self.application.go()
        logger.log.info("Server running.")

        while self.running:
            try:
                input("")
            except:
                self.stop()
                break

        self.sniffer.stop()
        self.analyser.stop()
        self.analyser.join(timeout=5)
        logger.log.info("Server stoped.")
        logger.log.stop()

    def stop(self):
        """Stop the server and its modules"""
        self.running = False
