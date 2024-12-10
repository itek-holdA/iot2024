from machine import Pin                       # Pin
from gpio_lcd import GpioLcd                  # LCD Modul til ???
import lcd_api                                # LCD API
import time                                   # Time
from nonblockingtimer import NonBlockingTimer # Non blocking timer klasse
from lmt87 import LMT87                       # Onboard temp-sensor på Educaboard
from hcsr04 import HCSR04
from machine import UART
from gps_simple import GPS_SIMPLE

# LMT87 Variabler
pin_lmt87 = 35
t1 = 25.2
adc1 = 2659
t2 = 24.2
adc2 = 2697
temp = LMT87(pin_lmt87)

# GPS Variabler
gps_port = 2                                 # ESP32 UART port, Educaboard ESP32 default UART port
gps_speed = 9600                             # UART speed, defauls u-blox speed

#########################################################################

batteri_char = bytearray([0b01110, 0b10001, 0b10001, 0b11001, 0b11101, 0b11111, 0b11111, 0b11111])



# Objekter
lcd = GpioLcd(rs_pin=Pin(27),          #Thingsboard skærm
              enable_pin=Pin(25),
              d4_pin=Pin(33),
              d5_pin=Pin(32),
              d6_pin=Pin(21),
              d7_pin=Pin(22),
              num_lines=4,
              num_columns=20)

acc_timer = NonBlockingTimer(100)      # Accelerations-læsnings objekt med et non-blocking delay
gps_timer = NonBlockingTimer(1000)      # GPS positionerings objekt med et non-blocking delay
temp_timer = NonBlockingTimer(1000)    # Temperatur målings objekt med et non-blocking delay
battery_timer = NonBlockingTimer(10000)

sensor_back = HCSR04(15, 34)           # Sensor Objekt #1  

uart = UART(gps_port, gps_speed)       # UART object creation
gps = GPS_SIMPLE(uart)                 # GPS object creation

# Metode til temperaturlæsning, plus print i konsollen
def temp_reading():
    adc_val = temp.get_adc_value()
    temperature = temp.get_temperature()
    print("Temp: %d °C <- %d" % (temperature, adc_val))
    lcd.move_to(0,0)
    lcd.putstr(f'Temp:{int(temperature)}C')

# Metode til GPS-Kordinater og hastighed, plus print i konsollen
def cords_speed():
    if gps.receive_nmea_data():
        lcd.move_to(0,1)
        lcd.putstr(f'X:{gps.get_latitude()} Y:{gps.get_longitude()}')
        lcd.move_to(0,2)
        lcd.putstr(f'{int(gps.get_speed())} KM/T')
        print(f"GPS Test")
    else:
        lcd.move_to(0,1)
        lcd.putstr(f'Opretter GPS-forbindelse')

def battery():
    lcd.move_to(19,0)
    lcd.custom_char(0, batteri_char)
    lcd.putchar(chr(0))
    lcd.move_to(16,0)
    lcd.putstr(f'99%')

while True:
    
    # Temperatur læsning med en non-blocking timer
    temp_timer.non_blocking_timer(temp_reading)
    
    # Koordinat og hastighedslæsning med en non-blocking timer
    gps_timer.non_blocking_timer(cords_speed)
    
    #
    battery_timer.non_blocking_timer(battery)