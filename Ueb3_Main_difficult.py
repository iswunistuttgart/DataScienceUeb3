import CommunicationManager as CM
import MachineLearningManager as ML
import threading
import time

# [Aufgabe3] Kommunikationsparameter erstellen und eintragen
# [Aufgabe3] [Aufgabe4] Helferklassen instanziieren

#[Vorgegeben] Prediction Thread Erstellung.
__startPredicitingThread = None

# [Aufgabe3] [Aufgabe4] [Aufgabe5]  Zyklische Vorhersage der Fehler durch die Modelle
def __PredictErrors():
    t = threading.currentThread()
    while getattr(t, "do_run", True):
		#TODO Implementierung

#[Vorgegeben] Prediction Thread Zuweisung
__startPredicitingThread = threading.Thread(target=__PredictErrors, args=(), name="StartPredicting")


#[Aufgabe4] Methode für die Interpretation von Modell-Vorhersagen implementieren
def handleResults('...'):
    

# [Aufgabe3] [Aufgabe4] Daten erfassen, speichern, Modelle vorbereiten und Prediction starten
def startProgram():


print("Program Running")
print("Sie haben folgende Optionen:")
print("0 : Programm beenden")
print("1 : Programm starten")
print("2 : Lichter unter 5A ausschalten")
print("3 : Licht unter 5A auf Grün setzen")
__Run = True


while __Run == True:
    try:
        #[Aufgabe3] [Aufgabe4] Benutzereingabe erfassen und auswerten
        
    except ValueError as e:
        print('ValueError:', 'Bitte eine Zahl eingeben!')

