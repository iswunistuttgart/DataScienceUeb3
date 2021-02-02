import sys
import time
import os
import csv
from datetime import *
import logging

from opcua import ua, Server
from threading import Thread
import paho.mqtt.client as mqtt

class NuelleSim():
    
    def __init__(self):
        """
        """
        self.mqttURL = "127.0.0.1"
        self.mqttPort = 1883
        self.mqttTimeout = 60
        self.opcUaAddress = "opc.tcp://127.0.0.1:4840"
        self.__stopFlag = False
        self.__threadSimOPCUA = Thread(target = self.__simLoopOPCUA, args=(),name="__simLoopOPCUA")
        self.__threadSimMQTT = Thread(target = self.__simLoopMQTT, args=(),name="__simLoopMQTT")

    def readRecordings(self,fileOPCUA,fileMQTT):
        # Read csv
        self.recordingListOPCUA = []
        self.recordingListMQTT = []
        fOPCUA = open(fileOPCUA, 'r') 
        linesOPCUA = fOPCUA.readlines() 
        for line in linesOPCUA: 
            row = line.rstrip().split(":::")
            timeRecord = datetime.strptime(row[2], '%H:%M:%S.%f')
            self.recordingListOPCUA.append((row[0],row[1],timeRecord,row[3]))
        
        fMQTT = open(fileMQTT, 'r') 
        linesMQTT = fMQTT.readlines() 
        for line in linesMQTT: 
            row = line.rstrip().split(":::")
            timeRecord = datetime.strptime(row[2], '%H:%M:%S.%f')
            self.recordingListMQTT.append((row[0],row[1],timeRecord))
        
    def __startOpcUAServer(self):
         # setup our server
        self.OpcUaserver = Server()
        self.OpcUaserver.set_endpoint(self.opcUaAddress)
        #Setupnamespace by hand
        self.OpcUaserver.set_application_uri("urn:SIMATIC.S7-1500.OPC-UAServer:Master-PLC")
        self.OpcUaserver.register_namespace("urn:SIMATIC.S7-1500.OPC-UAServer:Master-PLC")
        self.OpcUaserver.register_namespace("http://opcfoundation.org/UA/DI/")
        idx = self.OpcUaserver.register_namespace("http://www.siemens.com/simatic-s7-opcua")
        objects = self.OpcUaserver.get_objects_node()
        Masterplc = objects.add_object(idx, "Master-PLC")
        Masterplc.add_folder(idx,"Counters")
        DBglobal = Masterplc.add_folder(idx,"DataBlocksGlobal")
        Masterplc.add_folder(idx,"DataBlocksInstance")

        DB_OPC_UA = DBglobal.add_object('ns=3;s="DB_OPC_UA"',"DB_OPC_UA")
        DB_OPC_UA_GLOBAL_DATEN = DB_OPC_UA.add_variable('ns=3;s="DB_OPC_UA"."GLOBAL_DATEN"',"GLOBAL_DATEN",'ns=0,i=10')
        DB_OPC_UA_GLOBAL_DATEN.add_variable('ns=3;s="DB_OPC_UA"."GLOBAL_DATEN"."Systemdruck"',"Systemdruck", 'ns=0,i=10')
        DB_OPC_UA_QI = DB_OPC_UA.add_variable('ns=3;s="DB_OPC_UA"."Qi_CHARGER"',"Qi_CHARGER",'ns=0,i=10')
        DB_OPC_UA_QI.add_variable('ns=3;s="DB_OPC_UA"."Qi_CHARGER"."Ladetemperatur_PT100"',"Ladetemperatur_PT100",'ns=0,i=10')
        DB_OPC_UA_QI.add_variable('ns=3;s="DB_OPC_UA"."Qi_CHARGER"."Luefter_ein"',"Luefter_ein",'ns=0,i=10')
        stations = [("IMS_1_M0000000",("I_IMS1_IL","I_IMS1_IR"),("Q_IMS1_QR","Q_IMS1_QS")),
                    ("IMS_3A_M0009680",("I_IMS3A_B3","I_IMS3A_B4","I_IMS3A_IL","I_IMS3A_IR"),("Q_IMS3A_M1","Q_IMS3A_M2","Q_IMS3A_QR","Q_IMS3A_QS")),
                    ("IMS_3B_M0009680",("I_IMS3B_B3","I_IMS3B_B4","I_IMS3B_IL","I_IMS3B_IR"),("Q_IMS3B_M1","Q_IMS3B_M2","Q_IMS3B_QR","Q_IMS3B_QS")),
                    ("IMS_4A_M0009681",("I_IMS4A_B3","I_IMS4A_B4","I_IMS4A_IL","I_IMS4A_IR"),("Q_IMS4A_M1","Q_IMS4A_M2","Q_IMS4A_QR","Q_IMS4A_QS")),
                    ("IMS_4B_M0009681",("I_IMS4B_B3","I_IMS4B_B4","I_IMS4B_IL","I_IMS4B_IR"),("Q_IMS4B_M1","Q_IMS4B_M2","Q_IMS4B_QR","Q_IMS4B_QS")),
                    ("IMS_5A_M0009682",("I_IMS5A_B3","I_IMS5A_B4","I_IMS5A_B5","I_IMS5A_B6","I_IMS5A_IL","I_IMS5A_IR"),("Q_IMS5A_M1","Q_IMS5A_M2","Q_IMS5A_QR","Q_IMS5A_QS")),
                    ("IMS_5B_M0009682",("I_IMS5B_B3","I_IMS5B_B4","I_IMS5B_B5","I_IMS5B_B6","I_IMS5B_IL","I_IMS5B_IR"),("Q_IMS5B_M1","Q_IMS5B_M2","Q_IMS5B_QR","Q_IMS5B_QS")),
                    ("IMS_7_M0000000",("I_IMS7_B3","I_IMS7_B4","I_IMS7_B5","I_IMS7_B6","I_IMS7_B7","I_IMS7_IL","I_IMS7_IR"),("Q_IMS7_M1","Q_IMS7_M2","Q_IMS7_M3","Q_IMS7_M4","Q_IMS7_QR","Q_IMS7_QS"))  ]
        for stat in stations:
            node = DB_OPC_UA.add_variable('ns=3;s="DB_OPC_UA"."'+stat[0]+'"' ,stat[0],'ns=0,i=1')
            inn = node.add_variable('ns=3;s="DB_OPC_UA"."'+stat[0]+'"."I_Eingaenge"',"I_Eingaenge",'ns=0,i=1')
            for i in stat[1]:
                inn.add_variable('ns=3;s="DB_OPC_UA"."'+stat[0]+'"."I_Eingaenge"."'+i+'"',i,'ns=0,i=1')
            oun = node.add_variable('ns=3;s="DB_OPC_UA"."'+stat[0]+'"."Q_Ausgaenge"',"Q_Ausgaenge",'ns=0,i=1')
            for q in stat[2]:
                oun.add_variable('ns=3;s="DB_OPC_UA"."'+stat[0]+'"."Q_Ausgaenge"."'+q+'"',q,'ns=0,i=1')
        self.OpcUaserver.start()
    def __stopOpcUAServer(self):
        self.OpcUaserver.stop()
    def __startMqtt(self):
        self.mqttClient = mqtt.Client()
        self.mqttClient.connect(self.mqttURL, self.mqttPort, self.mqttTimeout)
    def __stoptMqtt(self):
        try:
            self.mqttClient.disconnect()
            logging.info('Disconnected successfully')
        except:
            logging.error('Disconnect from MQTT Broker failed')
            self.__threadMQTT.join()

    def start(self):
        self.__startOpcUAServer()
        self.__startMqtt()
        self.__threadSimOPCUA.start()
        self.__threadSimMQTT.start()

    def stop(self):
        self.__stopFlag = True
        self.__stopOpcUAServer()
        self.__stoptMqtt()

    def __simLoopOPCUA(self):
        while not self.__stopFlag:
            startTime = datetime.now()
            for rec in self.recordingListOPCUA:
                while not self.__stopFlag:
                    curTime = datetime.now()
                    timeDiff = curTime-startTime
                    timeRecord = rec[2]
                    if(timeDiff>=timedelta(hours=timeRecord.hour, minutes=timeRecord.minute, seconds=timeRecord.second,microseconds=timeRecord.microsecond)):
                        value = rec[1]
                        valueType = rec[3]
                        if valueType == "float":
                            value = float(rec[1])
                        elif valueType == "int":
                            value = int(rec[1])
                        elif valueType == "bool":
                            if rec[1] == '0':
                                value = False
                            if rec[1] == '1':
                                value = True
                        self.OpcUaserver.get_node(rec[0]).set_value(value)
                        break
    def __simLoopMQTT(self):
        while not self.__stopFlag:
            startTime = datetime.now()
            for rec in self.recordingListMQTT:
                while not self.__stopFlag:
                    curTime = datetime.now()
                    timeDiff = curTime-startTime
                    timeRecord = rec[2]
                    if(timeDiff>=timedelta(hours=timeRecord.hour, minutes=timeRecord.minute, seconds=timeRecord.second,microseconds=timeRecord.microsecond)):
                        ret = self.mqttClient.publish(rec[0],rec[1]) 
                        break
           

if __name__ == "__main__":

    ns = NuelleSim()
    fileOPCUA = os.path.dirname(os.path.abspath(__file__))  + "\\opcuaRecordings_201217_v1.csv"
    fileMQTT = os.path.dirname(os.path.abspath(__file__))  + "\\mqttRecordings_201217_v1.csv"
    
    ns.readRecordings(fileOPCUA,fileMQTT)
    ns.start()

    print("Press enter to stop")
    input()
    
    ns.stop()
   

    
   
    
    
