import logging
import queue
from threading import Thread

logging.disable(logging.WARNING)
import paho.mqtt.client as mqtt
import time
from opcua import Client
from opcua import ua


######### Common data ###########
class NuelleData:
    combinedData = []

    def __init__(self):
        self.combinedData = [0, 0, 0, 0, 0, 0, 0]


class SubHandler(object):

    def __init__(self, queue, Station5APresent):
        self.queue = queue
        self.station5APresent = Station5APresent
        self.ejected = False

    def datachange_notification(self, node, val, data):
        if (str(node.nodeid)=='StringNodeId(ns=3;s="DB_OPC_UA"."IMS_5A_M0009682"."I_Eingaenge"."I_IMS5A_IL")'):
            if (val == True):
                pass
                #self.station5APresent[0] = True
        if (str(node.nodeid)=='StringNodeId(ns=3;s="DB_OPC_UA"."IMS_5A_M0009682"."I_Eingaenge"."I_IMS5A_B4")'):
            if (self.ejected == False and val == False):
                self.ejected = True
                self.station5APresent[0] = True
            elif (self.ejected == True and val == True):
                self.ejected = False
                self.station5APresent[0] = False

        self.queue.put((str(node.nodeid), str(val)))



class CommunicationManager():

    def __init__(self, swtid="001",configObject=None):
        self.swtID = swtid
        self.mqttClient = None
        self.opcClient = None
        self.__stopFlag = False
        self.__valueQueue = queue.Queue()
        self.__startMQTTThread = Thread(target=self.__MQTT_startClient, args=(), name="StartMqttClient")
        self.__startOpcuaThread = None
        self.__startOpcuaWrite = None
        self.__nodeList = ["Wrong", "Entries"]
        self.__combinedNuelleData = NuelleData()
        self.Station5APresent = [False]

    ######### MQTT Methods ###########


    def __on_message(self, mqttc, obj, msg):
        # statt topic wahrscheinlich topic+fieldname, als Payload Feld6-8 aus den einzelnen topics (10 verschiedene features insg)
        self.__valueQueue.put((msg.topic, msg.payload.decode()))   #msg.payload is bytes, use "decode()" turn it into string.   do not use str()

    def MQTT_CreateClient(self, url, port, timeout):
        self.mqttClient = mqtt.Client()
        self.mqttClient.on_message = self.__on_message
        self.mqttClient.connect(url, port, timeout)

    def MQTT_subscribeToTopic(self, topics):
        for topic in topics:
            self.mqttClient.subscribe(topic, 0)

    def MQTT_startClient(self):
        self.__startMQTTThread = Thread(target=self.__MQTT_startClient, args=(), name="StartMqttClient")
        self.__startMQTTThread.start()

    def __MQTT_startClient(self):
        self.mqttClient.loop_forever()

    def MQTT_stopClient(self):
        self.__MQTT_stopClient()

    def __MQTT_stopClient(self):
        try:
            self.mqttClient.disconnect()
            logging.info('Disconnected successfully')
        except:
            logging.error('Disconnect from MQTT Broker failed')
        self.__startMQTTThread.join()

    ######### OPC UA Methods ###########

    def OPCUA_createClient(self, url):
        self.opcClient = Client(url)
        self.opcClient.connect()
        logging.info("Client is now connected to " + url)

    def OPCUA_subscribe(self, nodeList):
        self.__nodeList = nodeList
        self.__startOpcuaThread = Thread(target=self.__OPCUA_subscribe, args=(), name="StartOPCUAClient")
        self.__startOpcuaThread.start()

    def OPCUA_write(self, nodeIDtoWrite, valueToWrite):
        self.__startOpcuaWriteThread = Thread(target=self.__OPCUA_write, args=(nodeIDtoWrite, valueToWrite),
                                              name="WriteToOPCUAClient"+str(nodeIDtoWrite))
        self.__startOpcuaWriteThread.start()
        self.__startOpcuaWriteThread.join()

    def __OPCUA_write(self, nodeID, value):
        var = self.opcClient.get_node(nodeID)
        var.set_attribute(ua.AttributeIds.Value, ua.DataValue(value))

    def __OPCUA_subscribe(self):
        handler = SubHandler(self.__valueQueue,self.Station5APresent)
        self.__subscription = self.opcClient.create_subscription(50, handler)
        for i in range(len(self.__nodeList)):
            node = self.opcClient.get_node(self.__nodeList[i])
            self.__subscription.subscribe_data_change(node)

    def OPCUA_stopClient(self):
        self.__OPCUA_stopClient()

    def __OPCUA_stopClient(self):
        try:
            self.__subscription.delete()
            self.opcClient.disconnect()
            print('Disconnected successfully')
        except:
            print('Disconnect from opc ua server failed')

    ########## Handle Data Collection, Combination and Retrieving ###########

    def __addToNuelleData(self, ValueName, newValue):
        if ValueName == 'esp32mag':
            #print(newValue)
            newValue = list(newValue.split(","))
            if(newValue[1]==self.swtID):
                # print(newValue)
                self.__combinedNuelleData.combinedData[0] = float(newValue[5]) #feld 6 xmag
                self.__combinedNuelleData.combinedData[1] = float(newValue[6]) #feld 7 ymag
                self.__combinedNuelleData.combinedData[2] = float(newValue[7]) #feld 8 zmag
                self.__combinedNuelleData.combinedData[3] = newValue[4] #timestamp
        elif ValueName == 'StringNodeId(ns=3;s="DB_OPC_UA"."IMS_5A_M0009682"."I_Eingaenge"."I_IMS5A_IL")':
            self.__combinedNuelleData.combinedData[5] = newValue
        elif ValueName == 'StringNodeId(ns=3;s="DB_OPC_UA"."IMS_5A_M0009682"."I_Eingaenge"."I_IMS5A_B4")':
            self.__combinedNuelleData.combinedData[6] = newValue
        else:
            # pass
            print("Warnung - Unbekannte Variable erhalten: " + newValue + "    -     " + ValueName)

    def getDataSnapshot(self):
        return self.__combinedNuelleData.combinedData

    def __insertVariables(self):
        while not self.__stopFlag:
            if (not self.__valueQueue.empty()):
                queueContent = self.__valueQueue.get()
                self.__addToNuelleData(queueContent[0], queueContent[1])
                self.__valueQueue.task_done()

    def startCollectingData(self):
        for i in range(20):
            self.__insertVariablesThread = Thread(target=self.__insertVariables, args=(), name="insertVariables{0}".format(i))
            self.__insertVariablesThread.start()

    def stopCollectionData(self):
        self.__stopFlag = True
        self.__insertVariablesThread.join()

    def writeStation(self, address, value):
        self.OPCUA_write(address, value)

    def resetStation(self, number):
        for address in StationLightNode[number].values():
            self.OPCUA_write(address, False)
            print(address, "False")

    def endofProgramm(self):
        for LightDict in StationLightNode[1:]:
            self.OPCUA_write(LightDict['IDofGreen'], True)
            self.OPCUA_write(LightDict['IDofOrange'], False)
            self.OPCUA_write(LightDict['IDofRed'], False)
        print("Writes Done")
        time.sleep(2)
        self.stopCollectionData()
        print("Stoped Collecting")
        self.OPCUA_stopClient()
        print("Stoped OPCUA")
        self.MQTT_stopClient()
        print("Stoped MQTT")
        print("Stopped!")



# NodeID in dictionary
StationLightNode = [None] * 9  # 8 = Number of Stations +1

# Node ID of three lights at Station 1
StationLightNode[1] = {
    'IDofGreen': 'ns=3;s="DB_OPC_Meldesignale"."IMS_1_Meldungen"."LampeGruen"',
    'IDofOrange': 'ns=3;s="DB_OPC_Meldesignale"."IMS_1_Meldungen"."LampeGelb"',
    'IDofRed': 'ns=3;s="DB_OPC_Meldesignale"."IMS_1_Meldungen"."LampeRot"'
}

# Node ID of three lights at Station 3A
StationLightNode[2] = {
    'IDofGreen': 'ns=3;s="DB_OPC_Meldesignale"."IMS_3A_Meldungen"."LampeGruen"',
    'IDofOrange': 'ns=3;s="DB_OPC_Meldesignale"."IMS_3A_Meldungen"."LampeGelb"',
    'IDofRed': 'ns=3;s="DB_OPC_Meldesignale"."IMS_3A_Meldungen"."LampeRot"'
}

StationLightNode[3] = {  # 3B
    'IDofGreen': 'ns=3;s="DB_OPC_Meldesignale"."IMS_3B_Meldungen"."LampeGruen"',
    'IDofOrange': 'ns=3;s="DB_OPC_Meldesignale"."IMS_3B_Meldungen"."LampeGelb"',
    'IDofRed': 'ns=3;s="DB_OPC_Meldesignale"."IMS_3B_Meldungen"."LampeRot"'
}

StationLightNode[4] = {  # 4A
    'IDofGreen': 'ns=3;s="DB_OPC_Meldesignale"."IMS_4A_Meldungen"."LampeGruen"',
    'IDofOrange': 'ns=3;s="DB_OPC_Meldesignale"."IMS_4A_Meldungen"."LampeGelb"',
    'IDofRed': 'ns=3;s="DB_OPC_Meldesignale"."IMS_4A_Meldungen"."LampeRot"'
}

StationLightNode[5] = {  # 4B
    'IDofGreen': 'ns=3;s="DB_OPC_Meldesignale"."IMS_4B_Meldungen"."LampeGruen"',
    'IDofOrange': 'ns=3;s="DB_OPC_Meldesignale"."IMS_4B_Meldungen"."LampeGelb"',
    'IDofRed': 'ns=3;s="DB_OPC_Meldesignale"."IMS_4B_Meldungen"."LampeRot"'
}

StationLightNode[6] = {  # 5A
    'IDofGreen': 'ns=3;s="DB_OPC_Meldesignale"."IMS_5A_Meldungen"."LampeGruen"',
    'IDofOrange': 'ns=3;s="DB_OPC_Meldesignale"."IMS_5A_Meldungen"."LampeGelb"',
    'IDofRed': 'ns=3;s="DB_OPC_Meldesignale"."IMS_5A_Meldungen"."LampeRot"'
}

StationLightNode[7] = {  # 5B
    'IDofGreen': 'ns=3;s="DB_OPC_Meldesignale"."IMS_5B_Meldungen"."LampeGruen"',
    'IDofOrange': 'ns=3;s="DB_OPC_Meldesignale"."IMS_5B_Meldungen"."LampeGelb"',
    'IDofRed': 'ns=3;s="DB_OPC_Meldesignale"."IMS_5B_Meldungen"."LampeRot"'
}

StationLightNode[8] = {  # 7
    'IDofGreen': 'ns=3;s="DB_OPC_Meldesignale"."IMS_7_Meldungen"."LampeGruen"',
    'IDofOrange': 'ns=3;s="DB_OPC_Meldesignale"."IMS_7_Meldungen"."LampeGelb"',
    'IDofRed': 'ns=3;s="DB_OPC_Meldesignale"."IMS_7_Meldungen"."LampeRot"'
}
