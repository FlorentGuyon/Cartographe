# -*- coding: utf-8 -*-

from os import rename
from datetime import datetime
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

        self.dir_ = "./log/"
        self.file_format = "log"
        self.file_path = f'{self.dir_}{today}__0_0_0_0_0.{self.file_format}'

        formatter = Formatter("%(asctime)s    %(levelname)s    %(message)s")
        files = [file.name for file in Path(self.dir_).glob(f'*.{self.file_format}')]
        log_file_exists = list(filter(lambda name: today in name, files))

        if len(log_file_exists) > 0:
            existing_file_path = f"{self.dir_}{log_file_exists[0]}"
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
                    map(lambda str_: int(str_), stats.split('_')))

            rename(existing_file_path, self.file_path)

        file_handler = FileHandler(self.file_path)
        file_handler.setLevel(DEBUG)
        file_handler.setFormatter(formatter)

        LOGGER.setLevel(DEBUG)
        LOGGER.addHandler(file_handler)

        self.running = True

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
