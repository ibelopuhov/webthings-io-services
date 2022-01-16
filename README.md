# Some Things for Webthing.IO project

---
Disclamer: this is a personal project for home automation.

This is a repository of some services that represents things as a WebThingService
and can be deployed on RPI

## Installation

Services should be deployed to the virtual environment with python version 3.7+

First you have to create virtual environment and install requirements:
```shell
sudo apt-get install python3-venv
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
```

Next you can enable services from appropriate subfolders.
Each service has separate README file for additional installation instructions

Current services list:
* [thermometer](webthings_services/thermometer/README.md)
* [ups_thing](webthings_services/ups_thing/README.md)
