#!/usr/bin/python3

####################################################################################
#
# Bot Name: Smart Home
# Bot Username: GarageMi3bot
# https://www.codementor.io/garethdwyer/building-a-telegram-bot-using-python-part-1-goi5fncay
#
####################################################################################

# Pakete importieren
import json
import requests
from time import *
import time
import urllib
import RPi.GPIO as GPIO
import subprocess
import os
import sys

# Variablen für Token und URL definieren
TOKEN = "qwertz1234567890asdfghjkl0987654321"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

# Kontakte
USER1 = qwertz
USER2 = qwertz
USER3 = qwertz
USER4 = qwertz
USER5 = qwertz

# Admin bestimmen
ADMINID = USER1

# GPIO Einstellungen
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Liste der GPIO-Pins
GPIOS = [3, 5, 7, 11, 13, 15, 19, 21]

# GPIO-Pins aus "GPIOS" als angeschaltete Outputs festlegen
for i in range(0, 8):
    GPIO.setup(GPIOS[i], GPIO.OUT)
    GPIO.output(GPIOS[i], GPIO.HIGH)

# Datei "Log" resetten
Log = open("/home/pi/Desktop/Logfiles/Log.txt", "w")
Log.close()

# Datei "Log_last" resetten
Log_last = open("/home/pi/Desktop/Logfiles/Log_last.txt", "w")
Log_last.close()

# Definitionen
def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

# Abrufen der letzten Nachricht und der Chat-ID der Person
def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

# Antwort mit gleichem Text (Echo)
def echo_all(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        send_message(text, chat)

# Antwort mit Text "message"
def reply_with_message(updates, message):
    for update in updates["result"]:
        chat = update["message"]["chat"]["id"]
        send_message(message, chat)

# Nachricht an Sebastian (admin)
def message_to_owner(message):
    send_message(message, ADMINID)

# Nachricht schicken
def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    if reply_markup: #If-Bedingung wegen
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

# Namen aus der letzten Nachricht abrufen
def get_name(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    vorname = updates["result"][last_update]["message"]["chat"]["first_name"]
    try:
        nachname = updates["result"][last_update]["message"]["chat"]["last_name"]
        return(vorname, nachname) # Nachname und Vorname ausgeben
    except KeyError:
        return(vorname) # Nur Vorname ausgeben

# GPIO mit Telegram Message ansteuern (1s an)
def message_gpio_on_off(updates, gpio, ausgabe, antwort):
    print(ausgabe)
    reply_with_message(updates, antwort)
    gpio = int(gpio) - 1
    gpiopin = GPIOS[gpio]
    GPIO.output(gpiopin, GPIO.LOW)
    time.sleep(1)
    GPIO.output(gpiopin, GPIO.HIGH)

# GPIO mit Telegram Message an- bzw. abschalten
def message_gpio_zustand(updates, gpio, ausgabe, antwort, zustand):
    print(ausgabe)
    reply_with_message(updates, antwort)
    gpio = int(gpio) - 1
    gpiopin = GPIOS[gpio]
    GPIO.output(gpiopin, zustand)

# Custom Tastatur bauen
def build_keyboard(keyboard, status):
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": status}
    return json.dumps(reply_markup)
        
# Definition fur das Senden der Nachricht
def main():
    sperre = False
    root = False
    last_update_id = None
    zahl = 1
    logzähler = 1
    message_to_owner("Smart Home steht bereit!")
    while True:
        print(strftime("%d.%m.%Y, %H:%M:%S", localtime()))
        print("getting updates", zahl)
        print(" ")
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            print(strftime("%d.%m.%Y, %H:%M:%S", localtime()))
            print("Nachricht:", get_last_chat_id_and_text(updates)[0])
            name1 = get_name(updates)
            try:
                print("Von %s" %(name1))
            except TypeError:
                print("Von %s %s" %(name1))

# Nachrichteninformationen in Datei "Log" schreiben
            Log = open("/home/pi/Desktop/Logfiles/Log.txt", "a")
            Log.write(strftime("%d.%m.%Y, %H:%M:%S", localtime()))
            Log.write(": ")
            try:
                Log.write("%s" %(name1))
            except TypeError:
                Log.write("%s %s" %(name1))
            Log.write(": ")
            Log.write(get_last_chat_id_and_text(updates)[0])
            Log.write("\n")
            Log.close()

# Nachrichteninformationen in Datei "Log_all" schreiben
            Log_all = open("/home/pi/Desktop/Logfiles/Log_all.txt", "a")
            Log_all.write(strftime("%d.%m.%Y, %H:%M:%S", localtime()))
            Log_all.write(": ")
            try:
                Log_all.write("%s" %(name1))
            except TypeError:
                Log_all.write("%s %s" %(name1))
            Log_all.write(": ")
            Log_all.write(get_last_chat_id_and_text(updates)[0])
            Log_all.write("\n")
            Log_all.close()

# Nachrichteninformationen in Datei "Log_last" schreiben
            Log_last = open("/home/pi/Desktop/Logfiles/Log_last.txt", "a")
            Log_last.write(strftime("%d.%m.%Y, %H:%M:%S", localtime()))
            Log_last.write(": ")
            try:
                Log_last.write("%s" %(name1))
            except TypeError:
                Log_last.write("%s %s" %(name1))
            Log_last.write(": ")
            Log_last.write(get_last_chat_id_and_text(updates)[0])
            Log_last.write("\n")
            Log_last.close()
            logzähler += 1
            if logzähler >= 7:
                Log_last = open("/home/pi/Desktop/Logfiles/Log_last.txt", "r")
                lines = Log_last.readlines()
                Log_last.close()
                del lines[0]
                Log_last = open("/home/pi/Desktop/Logfiles/Log_last.txt", "w")
                for l in lines:
                    Log_last.write(l)
                Log_last.close()
                
# Nachricht weiterverarbeiten
            chatid = get_last_chat_id_and_text(updates)[1]
            chattextgross = get_last_chat_id_and_text(updates)[0]
            chattext = chattextgross.lower()
            splittext = chattext.split()
            splittextgross = chattextgross.split()
            bashtext = chattext.split(" ", 1)
            bashtextgross = chattextgross.split(" ", 1)

# Zugelassen für Sebastian, Dieter, Benjamin und Geli
            if chatid == USER1 or chatid == USER2 or chatid == USER3 or chatid == USER4:
                if chattext == "tor":
                    if sperre == False:
                        message_gpio_on_off(updates, 1, "Tor", "Befehl erkannt")
                    else:
                        reply_with_message(updates, "Garagentorsteuerung vom Admin gesperrt!")
                
# Tor mit Öffnungszeit
                elif splittext[0] == "tor" and len(splittext) == 2:
                    try:
                        if sperre == False:
                            wartezeit = 60 * min(abs(float(splittext[1])), 5) + 30
                            wartezeit = round(wartezeit)
                            if wartezeit < 60:
                                message_gpio_on_off(updates, 1, "Tor + Wartezeit (1)", "Tor wird für %s Sekunden geöffnet" %wartezeit)
                            else:
                                wartezeitminuten = wartezeit // 60
                                wartezeitsekunden = wartezeit % 60
                                if wartezeitsekunden == 0:
                                    if wartezeitminuten == 1:
                                        message_gpio_on_off(updates, 1, "Tor + Wartezeit (1)", "Tor wird für %s Minute geöffnet" %wartezeitminuten)
                                    else:
                                        message_gpio_on_off(updates, 1, "Tor + Wartezeit (1)", "Tor wird für %s Minuten geöffnet" %wartezeitminuten)
                                else:
                                    if wartezeitminuten == 1:
                                        if wartezeitsekunden == 1:
                                            message_gpio_on_off(updates, 1, "Tor + Wartezeit (1)", "Tor wird für %s Minute und %s Sekunde geöffnet" %(wartezeitminuten, wartezeitsekunden))
                                        else:
                                            message_gpio_on_off(updates, 1, "Tor + Wartezeit (1)", "Tor wird für %s Minute und %s Sekunden geöffnet" %(wartezeitminuten, wartezeitsekunden))
                                    else:
                                        if wartezeitsekunden == 1:
                                            message_gpio_on_off(updates, 1, "Tor + Wartezeit (1)", "Tor wird für %s Minuten und %s Sekunde geöffnet" %(wartezeitminuten, wartezeitsekunden))
                                        else:
                                            message_gpio_on_off(updates, 1, "Tor + Wartezeit (1)", "Tor wird für %s Minuten und %s Sekunden geöffnet" %(wartezeitminuten, wartezeitsekunden))
                            time.sleep(wartezeit)
                            message_gpio_on_off(updates, 1, "Tor + Wartezeit (2)", "Tor wird geschlossen")
                        else:
                            reply_with_message(updates, "Garagentorsteuerung vom Admin gesperrt!")
                    except ValueError:
                        reply_with_message(updates, "Kein Befehl erkannt")

# Tor nach Wartezeit
                elif splittext[0] == "tor" and splittext[1] == "in" and len(splittext) == 3:
                    try:
                        if sperre == False:
                            wartezeit = 60 * min(abs(float(splittext[2])), 5)
                            wartezeit = round(wartezeit)
                            if wartezeit < 60:
                                reply_with_message(updates, "Tor wird in %s Sekunden betätigt" %wartezeit)
                            else:
                                wartezeitminuten = wartezeit // 60
                                wartezeitsekunden = wartezeit % 60
                                if wartezeitsekunden == 0:
                                    if wartezeitminuten == 1:
                                        reply_with_message(updates, "Tor wird in %s Minute betätigt" %wartezeitminuten)
                                    else:
                                        reply_with_message(updates, "Tor wird in %s Minuten betätigt" %wartezeitminuten)
                                else:
                                    if wartezeitminuten == 1:
                                        if wartezeitsekunden == 1:
                                            reply_with_message(updates, "Tor wird in %s Minute und %s Sekunde betätigt" %(wartezeitminuten, wartezeitsekunden))
                                        else:
                                            reply_with_message(updates, "Tor wird in %s Minute und %s Sekunden betätigt" %(wartezeitminuten, wartezeitsekunden))
                                    else:
                                        if wartezeitsekunden == 1:
                                            reply_with_message(updates, "Tor wird in %s Minuten und %s Sekunde betätigt" %(wartezeitminuten, wartezeitsekunden))
                                        else:
                                            reply_with_message(updates, "Tor wird in %s Minuten und %s Sekunden betätigt" %(wartezeitminuten, wartezeitsekunden))
                            time.sleep(wartezeit)
                            message_gpio_on_off(updates, 1, "Tor in ...", "Tor wird betätigt")
                    except ValueError:
                        reply_with_message(updates, "Kein Befehl erkannt")
                elif splittext[0] == "nachricht" and len(bashtext) == 2: #Nachricht an Admin
                    adminnachricht = bashtextgross[1]
                    reply_with_message(updates, "Nachricht " + "'" + adminnachricht+ "'" + " wurde an Admin gesendet")
                    try:
                        name = "%s" %(name1)
                    except TypeError:
                        name = "%s %s" %(name1)
                    antwortid = chatid
                    adminnachricht = name + ": " + adminnachricht
                    message_to_owner(adminnachricht)
                elif splittext[0] == "anonym" and len(bashtext) == 2:
                    adminnachricht = bashtextgross[1]
                    antwortid = chatid
                    reply_with_message(updates, "Nachricht " + "'" + adminnachricht+ "'" + " wurde an Admin gesendet")
                    adminnachricht = "Anonym: " + adminnachricht
                    message_to_owner(adminnachricht)

# Tastatur für alle
                elif chattext == "tastatur" and chatid != ADMINID: # Tastatur mit "Tor" für Dieter, Benjamin und Geli
                    keyboard = build_keyboard([["Tor"], ["Tor 0", "Tor 1", "Tor 2"], ["Tor in 1", "Tor in 2", "Tor in 3"]], False)
                    send_message("Tastatur eingeblendet", chatid, keyboard)

# Eastereggs
                elif chattext == "42": # Easteregg 42
                    print("Easteregg 42")
                    reply_with_message(updates, "the answer to life the universe and everything")
                elif chattext == "pi": # Easteregg Pi
                    print("Easteregg Pi")
                    reply_with_message(updates, "3.14159 26535 89793 23846 26433 83279 50288 41971 69399 37510")

# Hilfe
                elif chattext == "?":
                    reply_with_message(updates, "Verfügbare Befehle: \n \n- Tor \n- Nachricht ... \n- Anonym ...")
                    if get_last_chat_id_and_text(updates)[1] == ADMINID:
                        reply_with_message(updates, "Nur für dich: \n \n- Temp \n- Ifconfig \n- Uptime \n- Log \n- Log last \n- Ping \n- Antwort ... \n- Sperre")
                        reply_with_message(updates, "Erweiterte Funktionen (Erreichbar mit 'root'): \n \n- Reboot \n- Shutdown \n- Stop \n- Bash ...")
                        reply_with_message(updates, "Eastereggs: \n \n- Pi \n- 42")

# Adminbereich nur zugelassen nur für Sebastian
                elif chatid == ADMINID:
                    if chattext == "temp" or chattext == "temperatur": # Temperaturausgabe
                        Temp = subprocess.Popen(["vcgencmd", "measure_temp"], stdout=subprocess.PIPE)
                        temp = Temp.stdout.read()
                        print("Temperatur:", temp)
                        reply_with_message(updates, temp)

                    elif splittext[0] == "antwort": # Antwort auf die letzte anonyme Nachricht ("Anonym") oder die letzte Nachricht eines anderen an mich ("Nachricht")
                        antwortnachricht = bashtextgross[1]
                        send_message(antwortnachricht, antwortid)
                        reply_with_message(updates, "Antwort wurde gesendet")

                    elif chattext == "tastatur": #Meine Tastatur
                        keyboard = build_keyboard([["Tor", "Temperatur", "Uptime"], ["Ifconfig", "Log last", "Benutzer"], ["Sperre", "Ping", "Root"]], False)
                        send_message("Tastatur eingeblendet", chatid, keyboard)

                    elif chattext == "benutzer":
                        keyboard = build_keyboard([["Tor"], ["Tor 0", "Tor 1", "Tor 2"], ["Tor in 1", "Tor in 2", "Tastatur"]], False)
                        send_message("Benutzertastatur eingeblendet", chatid, keyboard)

# Erweiterte Funktionen freischalten/sperren
                    elif chattext == "root":
                        if root == False:
                            root = True
                            keyboard = build_keyboard([["Reboot"], ["Shutdown"], ["Stop", "Root"]], False)
                            send_message("Erweiterte Funktionen freigeschaltet", chatid, keyboard)
                        else:
                            root = False
                            keyboard = build_keyboard([["Tor", "Temperatur", "Uptime"], ["Ifconfig", "Log last", "Benutzer"], ["Sperre", "Ping", "Root"]], False)
                            send_message("Erweiterte Funktionen gesperrt", chatid, keyboard)

# Bestimmte erweiterte Funktionen
                    elif chattext == "reboot":
                        if root == True:
                            reply_with_message(updates, "RasPi wird neugestartet")
                            os.system("reboot 0")
                        else:
                            reply_with_message(updates, "Erweiterte Funktionen gesperrt")
                    elif splittext[0] == "bash" and len(bashtext) == 2:
                        if root == True:
                            command = bashtext[1]
                            command = command.split()
                            Bash = subprocess.Popen(command, stdout=subprocess.PIPE)
                            bash = Bash.stdout.read()
                            reply_with_message(updates, bash)
                        else:
                            reply_with_message(updates, "Erweiterte Funktionen gesperrt")
                    elif chattext == "shutdown":
                        if root == True:
                            reply_with_message(updates, "RasPi wird heruntergefahren")
                            os.system("shutdown 0")
                        else:
                            reply_with_message(updates, "Erweiterte Funktionen gesperrt")
                    elif chattext == "stop":
                        if root == True:
                            reply_with_message(updates, "Programm wird beendet")
                            sys.exit(0)
                        else:
                            reply_with_message(updates, "Erweiterte Funktionen gesperrt")

# Normale Funktionen
                    elif chattext == "sperre":
                        if sperre == False:
                            sperre = True
                            reply_with_message(updates, "Garagentorsteuerung gesperrt")
                        else:
                            sperre = False
                            reply_with_message(updates, "Garagentorsteuerung entsperrt")
                    elif chattext == "ifconfig": # Netzwerkinformationen
                        Ifconfig = subprocess.Popen(["ifconfig"], stdout=subprocess.PIPE)
                        ifconfig = Ifconfig.stdout.read()
                        reply_with_message(updates, ifconfig)
                    elif chattext == "uptime": # Laufzeit
                        Uptime = subprocess.Popen(["uptime", "-p"], stdout=subprocess.PIPE)
                        uptime = Uptime.stdout.read()
                        reply_with_message(updates, uptime)
                    elif chattext == "log": # Logfile ab Programmstart
                        Log = open("/home/pi/Desktop/Logfiles/Log.txt")
                        logfile = Log.read()
                        reply_with_message(updates, logfile)
                        Log.close()
                    elif chattext == "log last": # Logfile der letzten 5 Nachrichten
                        Log = open("/home/pi/Desktop/Logfiles/Log_last.txt")
                        logfile = Log.read()
                        reply_with_message(updates, logfile)
                        Log.close()
                    elif chattext == "ping": # Ping an Google
                        reply_with_message(updates, "Bitte kurz warten...")
                        Ping = subprocess.Popen(["ping", "8.8.8.8", "-c", "5"], stdout=subprocess.PIPE)
                        ping = Ping.stdout.read()
                        reply_with_message(updates, ping)
                    else:
                        reply_with_message(updates, "Kein Befehl erkannt") # Sonstige Nachricht
                        print(updates)
                else:
                    reply_with_message(updates, "Kein Befehl erkannt") # Sonstige Nachricht
                    print(updates)

# Antwort an Raphael
            elif chatid == USER5:
                reply_with_message(updates, "Servus!")

# Antwort an alle anderen
            else:
                name2 = get_name(updates)
                try:
                    reply_with_message(updates, "Hallo %s %s, du bist nicht autorisiert!" %(name2)) # Für Personen mit Vor- und Nachname
                    print("Nicht autorisiert!")
                    print(updates)
                    nachricht = "%s %s wollte Zugriff." %(name2)
                    message_to_owner(nachricht) # Nachricht an Admin
                except TypeError:
                    reply_with_message(updates, "Hallo %s, du bist nicht autorisiert!" %(name2)) # Für Personen nur mit Vorname
                    print("Nicht autorisiert!")
                    print(updates)
                    nachricht = "%s wollte Zugriff." %(name2)
                    message_to_owner(nachricht) # Nachricht an Admin

# Jedes Mal
        zahl = zahl + 1
        print(" ")

# Senden
if __name__ == '__main__':
    main()

GPIO.cleanup()
