# Smart Agri Embedded AI 🌿

Système de monitoring agricole distribué.

### Matériel
- **Raspberry Pi 4** : Gateway MQTT + Contrôle Relais + Sonde NPK.
- **Tinker Board 2** : Vision par ordinateur (Détection de maladies).
- **Arduino Nano 33 BLE** : Capteur d'environnement TinyML.

### Installation Rapide
1. Installer `mosquitto` sur le RPi : `sudo apt install mosquitto`
2. Déployer `rpi-gateway/main.py`
3. Déployer `tinker-vision/inference.py` avec vos modèles TFLite.


smart-agri-embedded/
├── README.md              # Documentation globale et manuel de montage
├── .gitignore             # Fichiers à ignorer (modèles lourds, venv)
├── docker-compose.yml     # (Optionnel) Pour lancer MQTT et InfluxDB sur le RPi
│
├── rpi-gateway/           # LE CERVEAU (Raspberry Pi 4)
│   ├── main.py            # Orchestrateur (reçoit MQTT -> active relais)
│   ├── sensors_npk.py     # Lecture Modbus RS485
│   ├── actuators.py       # Contrôle GPIO (Pompe/Lumière)
│   └── requirements.txt
│
├── tinker-vision/         # L'EXPERT VISION (Tinker Board 2)
│   ├── inference.py       # Script de détection IA (TFLite/YOLO)
│   ├── models/            # Dossier pour vos fichiers .tflite
│   └── camera_utils.py    # Gestion du flux CSI
│
└── nano-sensor/           # LE SCOUT (Arduino Nano 33 BLE)
    ├── sensor_node.ino    # Code Arduino (TinyML + BLE/Serial)
    └── config.h           # Seuils et paramètres de capteurs