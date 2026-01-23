import cv2
import numpy as np
import time
import paho.mqtt.client as mqtt

# --- CONFIGURATION MQTT ---
# Utilisez l'IP de votre RPi pour plus de rapidité, ou gardez hivemq si le RPi y est aussi.
RP_IP = "broker.hivemq.com" 
TOPIC_VISION = "agri/vision/status"

client = mqtt.Client()

def connect_to_broker():
    try:
        client.connect(RP_IP, 1883, 60)
        print(f"MQTT: Connecté au broker {RP_IP}")
    except Exception as e:
        print(f"MQTT: Erreur de connexion : {e}")

connect_to_broker()

# --- CONFIGURATION CAMERA ---
cap = cv2.VideoCapture(5)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

last_sent = 0
mqtt_delay = 2 

print("Démarrage de l'analyse... (CTRL+C pour arrêter)")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erreur : Impossible de lire la caméra")
            time.sleep(1)
            continue

        # --- SEGMENTATION VERT ---
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Nettoyage
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # --- ANALYSE ---
        green_pixels = cv2.countNonZero(mask)

        if green_pixels > 5000:
            if time.time() - last_sent > mqtt_delay:
                try:
                    client.publish(TOPIC_VISION, "plante_detectee")
                    last_sent = time.time()
                    print(f"MQTT: Plante détectée ({green_pixels} px)")
                except:
                    print("Echec d'envoi MQTT, tentative de reconnexion...")
                    connect_to_broker()

        # Si vous avez un écran HDMI sur la Tinker Board, décommentez ci-dessous :
        # cv2.imshow("Detection", mask)
        # if cv2.waitKey(1) & 0xFF == ord('q'): break

except KeyboardInterrupt:
    print("\nArrêt du script.")
finally:
    cap.release()
    cv2.destroyAllWindows()
    client.disconnect()