# Cartographe

## Introduction

Cartographe is a WEB application for network cartography. It is host locally and developped in Python3.

## Preview

### Dashboard

![Dashboard Preview](https://raw.githubusercontent.com/FlorentGuyon/Cartographe/main/assets/img/cartographe_dashboard_1.png)
![Dashboard Preview](https://raw.githubusercontent.com/FlorentGuyon/Cartographe/main/assets/img/cartographe_dashboard_2.png)

### Vitals

![Vitals Preview](https://raw.githubusercontent.com/FlorentGuyon/Cartographe/main/assets/img/cartographe_vitals.png)

### Captures
![Captures Preview](https://raw.githubusercontent.com/FlorentGuyon/Cartographe/main/assets/img/cartographe_captures.png)

### Logs
![Logs Preview](https://raw.githubusercontent.com/FlorentGuyon/Cartographe/main/assets/img/cartographe_logs.png)

## Prerequisite
 * Python 3
      * Windows: Go on *[Python.org](https://www.python.org/downloads/)*, download the last version of Python 3 then execute the *.exe* file
      * Linux: Install the *python3* package, example:
        > yum update 
        > yum install -y python3

 * python3-devel
      * Linux: Install the *python3-devel* package, example:
        > yum install -y python3-devel

 * Wireshark
      * Windows: Go on *[Wireshark.org](https://www.wireshark.org/#download)*, download the last version of Wireshark then execute the *.exe* file
      * Linux: Install the *wireshark* package, example:
        > yum install -y wireshark

 * Git
      * Windows: Skip
      * Linux: Install the *wireshark* package, example:
        > yum install -y git



## Download
* Project
  * Windows: Download the project from this Github page (*Code > Download ZIP*) then extract the project from the .ZIP archive
  * Linux: Clone the repository from the Git package, example:
    > yum install -y git
    > git clone https://github.com/FlorentGuyon/Cartographe.git

 * Requirements:
   * Windows: 
     > pip3 install --user -r ...\\...\Cartographe\requirements.txt
   * Linux: 
     > pip3 install --user -r .../.../Cartographe/requirements.txt

## Configure
 * Edit the *config.txt* file
   * Windows:
     > tshark_path = C:\Program Files\Wireshark\tshark.exe
   * Linux:
     > vi .../.../Cartographe/config/config.txt
     > tshark_path = tshark

   *Do not modify lines starting with "default"*

## Run
 * Start the server
   * Windows:
     > py ...\\...\Cartographe\cartographe.py
   * Linux:
     > python3 .../.../Cartographe/cartographe.py

 * Open an internet browser and search for "*[localhost](http://127.0.0.1:80)*" in the address bar (unless you have previously edited the configuration file, therefore search for *http://<server_host>:<server_port>*)

 ## Compatibility
 |         | Windows | Linux | MacOS |
 | ------- |:-------:|:-----:|:-----:|
 | Firefox |   Yes   |   ?   |   ?   |
 | Chrome  |   Yes   |   ?   |   ?   |
 | Opera   |   Yes   |   ?   |   ?   |
 | IE      |   No    |   ?   |   ?   |

 ## Acknowledgements
 * This project is under *[GPL-3.0 License](https://github.com/FlorentGuyon/Cartographe/blob/main/LICENSE.md)*
 * This project is still under development
 * This project is not suitable for production environments
 * This project has educational purpose. It does not improve the security of your network nor your systems.