import urequests as requests
import network
import time
import gc
import secret

def Connect_Wifi(ssid, password):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)
    while station.isconnected() == False:
        pass
    print('Connection successful')
    print(station.ifconfig())