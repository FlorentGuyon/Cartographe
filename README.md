# Cartographe

## Introduction

Cartographe is a WEB application for network cartography. It is host locally and developped in Python3.

## Previews

### Dashboard

![Dashboard Preview](https://raw.githubusercontent.com/FlorentGuyon/Cartographe/main/assets/img/cartographe_dashboard_1.png)
![Dashboard Preview](https://raw.githubusercontent.com/FlorentGuyon/Cartographe/main/assets/img/cartographe_dashboard_2.png)

### Vitals

![Vitals Preview](https://raw.githubusercontent.com/FlorentGuyon/Cartographe/main/assets/img/cartographe_vitals.png)

### Captures
![Captures Preview](https://raw.githubusercontent.com/FlorentGuyon/Cartographe/main/assets/img/cartographe_captures.png)

### Logs
![Logs Preview](https://raw.githubusercontent.com/FlorentGuyon/Cartographe/main/assets/img/cartographe_logs.png)

## Prerequisites
 * Python 3
      * Windows (10): Go on *[Python.org](https://www.python.org/downloads/)*, download the last version of Python 3 then execute the *.exe* file
      * Linux (CentOS 8): As a user, install the *python3* package, example:
        > `sudo yum update -y`
        
        > `sudo yum install -y python3`


 * python3-devel
      * Windows (10): Skip
      
      * Linux (CentOS 8): As a user, install the *python3-devel* package, example:
        > `sudo yum install -y python3-devel`


 * GCC
      * Windows (10): Skip
      
      * Linux (CentOS 8): As a user, install the *gcc* package, example:
        > `sudo yum install -y gcc`


 * Wireshark
      * Windows (10): Go on *[Wireshark.org](https://www.wireshark.org/#download)*, download the last version of Wireshark then execute the *.exe* file (remember the installation path)
      
      * Linux (CentOS 8): As a user, install the *wireshark* package, example:
        > `sudo yum install -y wireshark`


 * Git
      * Windows (10): Skip
      
      * Linux (CentOS 8): As a user, install the *wireshark* package, example:
        > `sudo yum install -y git`


## Download
* Project
  * Windows (10): Download the project from this Github page (*Code > Download ZIP*) then extract the project from the .ZIP archive
  
  * Linux (CentOS 8): As a user, clone the repository withshut the Git package, example:
    > `git clone https://github.com/FlorentGuyon/Cartographe.git`


 * Requirements:
   * Windows (10): As a user, install the requirements:
     > `pip3 install --user -r Cartographe\requirements.txt`

   * Linux (CentOS 8): As a user, install the requirements:
     > `pip3 install --user -r Cartographe/requirements.txt`


## Configure
 * Edit the *config.txt* file
   * Windows (10): Add the absolute path to the *tshark.exe* file (wireshark installation path)
     > `tshark_path = C:\Program Files\Wireshark\tshark.exe`

   * Linux (CentOS 8): 
     * If you do not want to execute the program as root, use a *server_port* value above 1024
       > `server_port = 8080`

     * Add the absolute path to the *tshark* file or, if the package is accessible through the PATH variable, add directly the name of the package
       > `vi Cartographe/config/config.txt`

       > `tshark_path = tshark`

   *NB: Do not modify lines starting with "default"*
   
 * Add yourself in the *wireshark* group
   * Windows (10): Skip
   * Linux (CentOS 8): Add your username in the *wireshark* group and restart the system
     > `sudo usermod -a -G wireshark <username>`

     > `shutdown -r now`
    


## Run
 * Start the server
   * Windows (10):
     > `py Cartographe\cartographe.py`

   * Linux (CentOS 8):
     > `python3 Cartographe/cartographe.py`

 * Open an internet browser and search for "*[localhost](http://127.0.0.1:80)*" in the address bar (unless you have edited the configuration file, therefore search for *http://<server_host>:<server_port>*)

   *NB: Use the HTTP protocol, not the HTTPS protocol as there is no TLS Encryption configured* 


 ## Compatibilities
 |         | Windows 10 | CentOS 8 | MacOS |
 | ------- |:----------:|:--------:|:-----:|
 | Firefox |     Yes    |    Yes   |   ?   |
 | Chrome  |     Yes    |     ?    |   ?   |
 | Opera   |     Yes    |     ?    |   ?   |
 | IE      |     No     |     ?    |   ?   |
 

 ## Acknowledgements
 * *This project is under *[GPL-3.0 License](https://github.com/FlorentGuyon/Cartographe/blob/main/LICENSE.md)**
 * *This project is still under development and can hosts security issues*
 * *This project is not suitable for production environments*
 * *This project has educational purpose. It does not improve the security of your networks nor your systems.*
 * *This project can become harmful if it is modified by someone else.*