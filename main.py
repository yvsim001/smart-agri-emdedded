
import paho.mqtt.client as mqtt
from gpiozero import OutputDevice
from datetime import datetime
import minimalmodbus
import serial
import time


# ==============================
# CONFIGURATION HARDWARE
# ==============================
# Relais
POMPE = OutputDevice(17, active_high=False, initial_value=False)
LUMIERE = OutputDevice(27, active_high=False, initial_value=False)

# Sonde RS485 (Via adaptateur USB JZK)
try:
    sensor = minimalmodbus.Instrument('/dev/ttyUSB1', 1) # Adresse esclave 1
    sensor.serial.baudrate = 4800
    sensor.serial.timeout = 1
    print("RS485 : Adaptateur USB detecte")
except Exception as e:
    print(f"Erreur configuration RS485 : {e}")

# ==============================
# CONFIGURATION MQTT
# ==============================
MQTT_BROKER = "broker.hivemq.com" # Ou l'IP locale du RPi
TOPIC_VISION = "agri/vision/status"
TOPIC_MOISTURE = "agri/sensor/moisture"

# ==============================
# CALLBACKS MQTT
# ==============================
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("MQTT : Connecte avec succes")
        client.subscribe([(TOPIC_VISION, 0), (TOPIC_MOISTURE, 0)])
    else:
        print("MQTT : Echec de connexion, code :", reason_code)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"MQTT Message -> {msg.topic} : {payload}")

    # Logique IA Vision (Tinker Board)
    if msg.topic == TOPIC_VISION and payload == "besoin_eau":
        print("Action : IA Vision demande arrosage -> Pompe ON (2s)")
        POMPE.on()
        time.sleep(2)
        POMPE.off()

# ==============================
# INITIALISATION MQTT
# ==============================
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# ==============================
# BOUCLE PRINCIPALE (Lecture Capteur + MQTT)
# ==============================
try:
    print("Demarrage du systeme complet...")
    client.connect(MQTT_BROKER, 1883, 60)
    
    # On lance la boucle MQTT en arrirre-plan (non-bloquante)
    client.loop_start()

    while True:
        try:
            # =========================
            # GESTION LUMIERE 12H/JOUR
            # =========================
            heure_actuelle = datetime.now().hour

            if 8 <= heure_actuelle < 20:   # 8h ? 20h
                LUMIERE.on()
            else:
                LUMIERE.off()

            # =========================
            # LECTURE MODBUS
            # =========================
            val_humidite = sensor.read_register(0, 1) / 10.0
            val_temp     = sensor.read_register(1, 1) / 10.0
            val_ph       = sensor.read_register(3, 1) / 10.0
            
            print(f"[CAPTEUR] Hum: {val_humidite}% | Temp: {val_temp}C | pH: {val_ph}")

            # Publication MQTT
            client.publish(TOPIC_MOISTURE, str(val_humidite))

            # =========================
            # SECURITE ARROSAGE
            # =========================
            if val_humidite < 5.0:
                print("Alerte : Sol tres sec ! Arrosage de securite...")
                POMPE.on()
                time.sleep(5)
                POMPE.off()

        except Exception as e:
            print(f"RS485 : Erreur de lecture -> {e}")

        time.sleep(10)

except KeyboardInterrupt:
    print("Arret du systeme")
    client.loop_stop()
    POMPE.off()
    LUMIERE.off()
