import minimalmodbus
import serial
import time

# --- CONFIGURATION DU CAPTEUR ---
# L'adaptateur USB est généralement sur /dev/ttyUSB0
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1) # 1 est l'adresse esclave par defaut
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity   = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout  = 1  # secondes

def lire_donnees_sol():
    try:
        # Les registres dependent du modele exact (souvent 0x0000 a 0x0006)
        # Humidite (Registre 0), Temperature (Registre 1), EC (Registre 2), pH (Registre 3)
        humidite = instrument.read_register(0, 1) / 10.0
        temp = instrument.read_register(1, 1) / 10.0
        ec = instrument.read_register(2, 0)
        ph = instrument.read_register(3, 1) / 10.0
        
        return {
            "humidite": humidite,
            "temp": temp,
            "ec": ec,
            "ph": ph
        }
    except Exception as e:
        print(f"Erreur de lecture RS485 : {e}")
        return None

if __name__ == "__main__":
    while True:
        data = lire_donnees_sol()
        if data:
            print(f"Sol -> Hum: {data['humidite']}% | Temp: {data['temp']}C | pH: {data['ph']}")
        time.sleep(5)