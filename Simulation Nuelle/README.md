# nuellesim

## Required Software

* Python 3 or higher with pip [Download](https://www.python.org/downloads/release/python-391/)
* Python OPC UA: Execute `pip install opcua` in your shell. Shell must be started with admin rights.
* Python MQTT: Execute `pip install paho-mqtt` in your shell. Shell must be started with admin rights.
* MQTT Broker [Download](https://mosquitto.org/download/)

## Installation

Python 3: Execute the installer and make sure that python is added to your PATH variable and pip is checked for installation

MQTT: Download and install mqtt. Please add mqtt as a service by `C:\Program Files\mosquitto\mosquitto install`. Change the path to your installation folder.

PIP packages: Install opcua and paho-mqtt via pip `pip install opcua paho-mqtt`

## Execution

* Make sure, that the sim data (opcuaRecordings.csv and mqttRecordings.csv) is located in the same folder as the nuelleSim.py file
* Start the simulation by executing the `startSim.bat`

## Recording of sim data

* Configure the `dataRecording.py` in the `main()` function
* Start recording by execution `startRecording.bat`