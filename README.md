# Cartographe

## What is it ?

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

## How to download it ?

Clone the repository from this Github page

## How to install it ?

 * Make sure you have *[Python 3](https://www.python.org/downloads/)* installed on your system

> py -V

 * Make sure you have the *[pip3](https://pip.pypa.io/en/stable/installing/)* Python module installed on your system 

> pip3 -V

 * Make sure you have *[Wireshark](https://www.wireshark.org/#download)* installed on your system 

> "C:\Program Files\Wireshark\tshark.exe" -v

 * Install the required modules:

> pip3 install -r requirements.txt

## How to configure it ?

 * Edit the */config/config.txt* file. Do not edit the lines begining by "*default_...*"

 > tshark_path = C:\Program Files\Wireshark\tshark.exe

## How to run it ?

 * Run the *cartographe.py* file with Python 3:

> py cartographe.py
 
 * Open an internet browser and search for "*[localhost](http://127.0.0.1:80)*" in the address bar (unless you have previously edited the configuration file, therefore, search for *http://<server_host>:<server_port>*)