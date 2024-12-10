import network
from time import sleep

# Opret Wi-Fi-station og forbind til et netværk
sta = network.WLAN(network.STA_IF)
sta.active(True)

# Kontroller, om stationen er aktiv
if not sta.isconnected():
    print("Trying to connect...")
    sta.connect("", "")

    # Vent på forbindelse
    while not sta.isconnected():
        print("Connecting")
        sleep(0.5)

    if sta.isconnected():
        print("STA connected:", sta.ifconfig())
    else:
        print("Connection failed")

# Opret Access Point (Hotspot)
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="ESP32_Hotspot", password="12345678")

print("AP active:", ap.ifconfig())