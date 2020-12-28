# -*- coding: utf-8 -*-

import signal
from os import rename, stat, mkdir, path
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

    ready = None
    running = None
    queue = None
    file_name = None
    dir_ = None

    def __init__(self, queue, fix_files=False):
        """Initialize a Tshark based sniffer"""
        Thread.__init__(self)

        self.tshark_path = config.get("tshark_path")
        self.queue = queue
        self.dir_ = "./capture/"
        self.file_format = "pcap"
        self.ready = False
        self.running = False

        self.create_directory()

        if fix_files:
            self.fix_files()

        if self.check_tshark_path():
            self.ready = True
            logger.log.info("Sniffer ready.")

    def create_directory(self):
        """Try to create the capture directory"""
        try:
            mkdir(self.dir_)
            logger.log.info(f"The {self.dir_} directory is created.")

        except FileExistsError:
            pass

        except Exception as e:
            logger.log.error(e)

    def check_tshark_path(self):
        """Check if the path from the config file is valid"""
        check = path.isfile(self.tshark_path)

        if not check:
            logger.log.error(f"The path to the Tshark module ({self.tshark_path}) is not valid. Please edit the /config/config.txt file.")
            self.tshark_path = None 

        return check

    def get_files(self):
        """Get the list of file from the capture directory"""
        return sorted(Path(self.dir_).glob(f'*.{self.file_format}'))

    def fix_files(self):
        """Rename the corrupt file"""
        files = self.get_files()

        for file in files:
            if "__" not in file.name:
                continue

            last_modified_date = int(stat(file).st_mtime)
            new_file_name = file.name.replace("__", f"_{last_modified_date}_")

            try:
                rename(file, f"{self.dir_}{new_file_name}")

            except Exception as e:
                logger.log.error(e)

            else:
                logger.log.warning(
                    f'Capture file "{file.name}" not have an end time. This could mean that the last execution of the program stopped after a critical error and therefore the file was not closed properly. The file is renamed "{new_file_name}" according to its last modification date')

    def sniff(self, interface):
        """Start listening to a network interface"""
        if not self.ready:
            logger.log.error("The sniffer cannot start because it is not ready.")
            return False

        self.interface = interface
        self.running = True
        self.start()

    def run(self):
        """Get the tshark data and send them to the analyser"""

        now = int(datetime.now().timestamp())
        self.file_path = f'{self.dir_}{now}__{self.interface}.{self.file_format}'

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
            logger.log.info(f"Stop sniffing the {self.interface} interface.")

        # Add the end timestamp to the name of the file
        now = int(datetime.now().timestamp())
        new_name = self.file_path.replace("__", f'_{now}_')

        try:
            rename(self.file_path, new_name)

        except:
            logger.log.error(f"Capture file {self.file_path} is already open in another process and therefor cannot be rename to include the capture end time. The file will be corrected the next time the program is run.")

        logger.log.info("Sniffer stoped.")

    def stop(self):
        """Stop sniffing"""
        self.running = False
