# -*- coding: utf-8 -*-

from os import rename, mkdir, path
from datetime import datetime
from sys import argv
from pathlib import Path
from logging import Formatter, FileHandler, StreamHandler, getLogger, DEBUG, shutdown


LOGGER = getLogger("Logger")


class Logger():
    debug_count = None
    info_count = None
    warning_count = None
    error_count = None
    critical_count = None
    dir_ = None
    file_format = None
    file_path = None
    running = None
    recent_error_count = None

    def __init__(self):
        self.debug_count = 0
        self.info_count = 0
        self.warning_count = 0
        self.error_count = 0
        self.critical_count = 0
        self.recent_error_count = 0

        today = datetime.now().strftime("%d-%m-%Y")
        formatter = Formatter("%(asctime)s    %(levelname)s    %(message)s")

        self.dir_ = f"{path.abspath(path.dirname(argv[0]))}/log/"
        self.file_format = "log"
        self.file_path = f'{self.dir_}{today}__0_0_0_0_0.{self.file_format}'

        self.create_directory()

        todays_log_file = self.get_todays_log_file()

        if todays_log_file:
            existing_file_path = f"{self.dir_}{todays_log_file}"
            stats = existing_file_path.split("__")[1]
            stats = stats.split('.')[0]

            if stats == "0_0_0_0_0":
                with open(existing_file_path, 'r') as content:

                    for line in content:
                        level = line.split("    ")[1]

                        if level == "DEBUG":
                            self.debug_count += 1

                        elif level == "INFO":
                            self.info_count += 1

                        elif level == "WARNING":
                            self.warning_count += 1

                        elif level == "ERROR":
                            self.error_count += 1

                        elif level == "CRITICAL":
                            self.critical_count += 1

            else:
                self.debug_count, self.info_count, self.warning_count, self.error_count, self.critical_count = list(
                    map(lambda stat: int(stat), stats.split('_')))

            try:
                rename(existing_file_path, self.file_path)

            except Exception as e:
                print(e)
                self.file_path = existing_file_path

        file_handler = FileHandler(self.file_path)
        file_handler.setLevel(DEBUG)
        file_handler.setFormatter(formatter)

        LOGGER.setLevel(DEBUG)
        LOGGER.addHandler(file_handler)

        self.running = True

    def get_todays_log_file(self):
        """Rename the corrupt file"""   
        files = self.get_files()
        files_name = [file.name for file in files]
        today = datetime.now().strftime("%d-%m-%Y")
        todays_log_file = list(filter(lambda name: today in name, files_name))

        if len(todays_log_file) == 0:
            return None

        return todays_log_file[0]

    def create_directory(self):
        """Try to create the log directory"""
        try:
            mkdir(self.dir_)
            logger.log.info(f"The {self.dir_} directory is created.")

        except FileExistsError:
            pass

        except Exception as e:
            print(e)

    def get_files(self):
        """Get the list of file from the capture directory"""
        return sorted(Path(self.dir_).glob(f'*.{self.file_format}'))

    def debug(self, message):
        if self.running:
            self.debug_count += 1
            LOGGER.debug(message)

    def info(self, message):
        if self.running:
            self.info_count += 1
            LOGGER.info(message)

    def warning(self, message):
        if self.running:
            self.warning_count += 1
            self.recent_error_count += 1
            LOGGER.warning(message)

    def error(self, message):
        if self.running:
            self.error_count += 1
            self.recent_error_count += 1
            LOGGER.error(message)

    def critical(self, message):
        if self.running:
            self.critical_count += 1
            self.recent_error_count += 1
            LOGGER.critical(message)

    def get_recent_error_count(self):
        count = self.recent_error_count
        self.recent_error_count = 0
        return count

    def stop(self):
        self.running = False
        shutdown()
        stats = f"{self.debug_count}_{self.info_count}_{self.warning_count}_{self.error_count}_{self.critical_count}"
        file_path = self.file_path.split("__")[0]
        new_file_path = f"{file_path}__{stats}.{self.file_format}"
        rename(self.file_path, new_file_path)


log = Logger()
