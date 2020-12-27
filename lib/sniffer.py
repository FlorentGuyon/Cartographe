# -*- coding: utf-8 -*-

import signal
from os import rename, stat
from json import loads
from pathlib import Path

from datetime import datetime
from threading import Thread
from queue import Queue
from subprocess import Popen, PIPE

from . import logger
from . import config

config.load_config()


class Sniffer(Thread):

    running = False
    queue = None
    file_name = None

    def __init__(self, queue, fix_files=False):
        """Initialize a Tshark based sniffer"""
        Thread.__init__(self)
        self.tshark_path = config.get("tshark_path")
        self.queue = queue

        if fix_files:
            files = sorted(Path("./capture/").glob('*.pcap'))
            list(map(self.fix_file, files))

        logger.log.info("Sniffer ready.")

    def fix_file(self, file):
        """Rename the corrupt file"""
        if "__" in file.name:
            last_modified_date = int(stat(file).st_mtime)
            new_file_name = file.name.replace("__", f"_{last_modified_date}_")
            rename(file, f"./capture/{new_file_name}")
            logger.log.warning(
                "A corrupt file was found (and fixed) among the capture files. This may mean that the last program execution stopped after a critical error.")

    def sniff(self, interface):
        """Start listening to a network interface"""
        self.interface = interface
        self.running = True
        self.start()

    def run(self):
        """Get the tshark data and send them to the analyser"""
        if self.tshark_path is None:
            self.stop()
            return

        now = int(datetime.now().timestamp())
        self.file_path = f'./capture/{now}__{self.interface}.pcap'
        logger.log.info("Sniffer running.")

        with Popen([self.tshark_path, "-q", "-i", self.interface, "-l", "-T", "json", "-w", self.file_path], stdout=PIPE) as capture:
            packet = ""
            logger.log.info(f"Sniffing the {self.interface} interface.")

            while self.running:
                line = capture.stdout.readline().decode()
                if line == "[\r\n":
                    pass
                elif line == "  },\r\n":
                    packet += '}'
                    packet = loads(packet)
                    self.queue.put(packet)
                    packet = ""
                else:
                    packet += line.strip()
            capture.terminate()

        # Add the end timestamp to the name of the file
        now = int(datetime.now().timestamp())
        new_name = self.file_path.replace("__", f'_{now}_')

        try:
            rename(self.file_path, new_name)
        except:
            logger.log.error(f"The capture file {self.file_path} is already open in another process.")

        logger.log.info("Sniffer stoped.")

    def stop(self):
        """Stop sniffing"""
        self.running = False
