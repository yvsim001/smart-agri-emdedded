# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
from gpiozero import OutputDevice
import time

# ==============================
# CONFIGURATION HARDWARE
# ==============================
# active_high=False car la plupart des relais sont actifs Ã  l'Ã©tat bas
POMPE = OutputDevice(17, active_high=False, initial_value=False)
LUMIERE = OutputDevice(27, active_high=False, initial_value=False)

# ==============================
# CONFIGURATION MQTT
# ==============================
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

TOPIC_VISION = "agri/vision/status"
TOPIC_MOISTURE = "agri/sensor/moisture"

# ==============================
# CALLBACKS MQTT (API v2)
# ==============================
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connecte au broker MQTT avec succes")
        client.subscribe([
            (TOPIC_VISION, 0),
            (TOPIC_MOISTURE, 0)
        ])
    else:
        print("Echec de connexion MQTT, code :", reason_code)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print("Message recu ->", msg.topic, ":", payload)

    # ---- Gestion humidite (Arduino / sonde) ----
    if msg.topic == TOPIC_MOISTURE:
        try:
            humidite = float(payload)
            if humidite < 30.0:
                print("Humidite basse -> Pompe ON (5s)")
                POMPE.on()
                time.sleep(5)
                POMPE.off()
        except ValueError:
            print("Payload humidite invalide")

    # ---- Gestion vision IA ----
    if msg.topic == TOPIC_VISION:
        if payload == "besoin_eau":
            print("Vision: besoin eau -> Pompe ON (2s)")
            POMPE.on()
            time.sleep(2)
            POMPE.off()

# ==============================
# INITIALISATION CLIENT MQTT
# ==============================
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_message = on_message

# ==============================
# BOUCLE PRINCIPALE
# ==============================
try:
    print("Demarrage du systeme central (Clean Mode)")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

except KeyboardInterrupt:
    print("Arret du systeme")
    POMPE.off()
    LUMIERE.off()
