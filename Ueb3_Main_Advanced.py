import CommunicationManager as CM
import MachineLearningManager as ML
import threading
import time

# OPC UA
# [Aufgabe3] Parameter eintragen
OpcuaURL = ""
nodeIdsListUeb = [
    '...',
    '...'
]

# MQTT
# [Aufgabe3] Parameter eintragen
MqttUrl = ""
MqttPort = ""
MqttTimeout = 60
MqttTopics = [""]
WSTID = "001"

# [Aufgabe3,4] Objekte der Helferklassen instanziieren



#[Vorgegeben] Prediction Thread Erstellung
__startPredicitingThread = None


# [Aufgabe3] Array mit den Features für das Analyse Modell erstellen und füllen
# [Aufgabe4] Anschließend Modell für Vorhersagen nutzen und Antworten auswerten
# [Aufgabe5] Vorhersagen nur unter Station 5A ausführen
# [Aufgabe5] Vorhersage soll nach Verlassen der Station 5 weiterhin statisch angezeigt werden
# [Vorgegeben] 0.5 Sekunden Pause um eine zyklische Vorhersage der Modelle im 500ms Takt zu ermöglichen
def __PredictErrors():
    t = threading.currentThread()
    while getattr(t, "do_run", True):
		
        time.sleep(0.5) 

#[Vorgegeben] Prediction Thread Zuweisung (Keine Änderung nötig)
__startPredicitingThread = threading.Thread(target=__PredictErrors, args=(), name="StartPredicting")


#[Aufgabe3] Methode für die Interpretation von Modell-Vorhersagen implementieren
#[Aufgabe3] Mit OPC UA Write die Warnlampen ansprechen
def handleResults(predictionStift):
    if(predictionStift == [0]):
		pass
	#elif(...)
    
	
#[Aufgabe3] Clients erstellen und Subcription anlegen
#[Aufgabe3] Datenspeicherung starten
#[Aufgabe4] Modelle für die Nutzung vorbereiten
#[Vorgegeben] globalen PredictionThread in startProgram-Umgebung laden
#[Aufgabe3] __startPredicitingThread starten, um mit der zyklischen Analyse zu starten (nach Referenz auf globalen predictionThread)
def startProgram():
    global __startPredicitingThread
    


print("Program Running")
print("Sie haben folgende Optionen:")
print("0 : Programm beenden")
print("1 : Programm starten")
print("2 : Lichter unter 5A ausschalten")
print("3 : Licht unter 5A auf Grün setzen")
__Run = True


while __Run == True:
    try:
        #[Aufgabe3/4] Benutzereingabe erfassen
		
		# [Aufgabe4] Thread beenden
        # [Aufgabe3] Datenerfassung beenden
        # [Aufgabe4] Dieses Programm beenden
        if 'Benutzereingabe' == "0":
			
		# [Aufgabe3/4] Programm starten
        elif 'Benutzereingabe' == "1":
		
		# [Aufgabe4] Lichter unter 5A ausschalten		
        elif 'Benutzereingabe' == "2":
			
		# [Aufgabe4] Licht unter 5A auf Grün setzen
        elif 'Benutzereingabe' == "3":
			
        else:
            print('Bitte eine Zahl zwischen 0 und 3 eingeben!')
    except ValueError as e:
        print('ValueError:', 'Bitte eine Zahl eingeben!')

