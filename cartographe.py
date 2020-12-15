# -*- coding: utf-8 -*-

__author__ = "Florent Guyon"
__maintainer__ = "Florent Guyon"
__email__ = "florent.guyon@protonmail.com"
__status__ = "Development"
__version__ = "1.0"
__license__ = "GNU General Public Licence v3"
__credits__ = ["Florent Guyon"]


from lib.server import Server


def main():
    """Start the application"""
    server = Server()
    server.start()


if __name__ == '__main__':
    """Start the main function if the module is executed, not imported"""
    main()
