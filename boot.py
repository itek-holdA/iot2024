from machine import Pin
import network
from time import sleep
import secret
import lcd_api
from gpio_lcd import GpioLcd

lcd = GpioLcd(rs_pin=Pin(27),            # Thingsboard skærm
              enable_pin=Pin(25),
              d4_pin=Pin(33),
              d5_pin=Pin(32),
              d6_pin=Pin(21),
              d7_pin=Pin(22),
              num_lines=4,
              num_columns=20)


sta = network.WLAN(network.STA_IF)
sta.active(True)

if not sta.isconnected():
    lcd.clear
    lcd.move_to(0,0)
    lcd.putstr('Forbinder til Wi-Fi')
    sta.ifconfig(('192.168.0.30', '255.255.255.192', '192.168.0.1', '192.168.0.10'))
    sta.connect(secret.SSID, secret.PASSWORD)

    # Vent på forbindelse
    while not sta.isconnected():
        print("Connecting...")
        sleep(0.5)

if sta.isconnected():
    print("Forbundet til AP:", sta.ifconfig())
else:
    print("Forbindelse fejlede")