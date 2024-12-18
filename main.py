import lcd_api, lcd_warning, time, socket
from machine import Pin, UART, ADC, reset, I2C       # Machine-imports
from gpio_lcd import GpioLcd                         # LCD Modul til ???
from nonblockingtimer import NonBlockingTimer        # Non blocking timer klasse
from lmt87 import LMT87                              # Onboard temp-sensor på Educaboard
from gps_simple import GPS_SIMPLE                    # GPS
from uthingsboard.client import TBDeviceMqttClient   # Thingsboard
from battery_percentage import BatteryPercent
from adc_substitute import AdcSubstitute
from mpu6050 import MPU6050

i2c = I2C(0)
imu = MPU6050(i2c)

# Blindvinkelsensor Variabler
left = 0
right = 0
rear = 0

# GPS Variabler
gps_port = 2                                 
gps_speed = 9600                             

# Batteri Variabler
bat_perc = BatteryPercent()
battery_adc = AdcSubstitute(36)

r1 = 5100  
r2 = 3000
vin_max = 8.4

#I2C
mpu6050 = MPU6050(i2c)

batteri_char = bytearray([0b01110, 0b10001, 0b10001, 0b11001, 0b11101, 0b11111, 0b11111, 0b11111])

temp1 = 0

# Objekter
lcd = GpioLcd(rs_pin=Pin(27),            # Thingsboard skærm
              enable_pin=Pin(25),
              d4_pin=Pin(33),
              d5_pin=Pin(32),
              d6_pin=Pin(21),
              d7_pin=Pin(22),
              num_lines=4,
              num_columns=20)

acc_timer = NonBlockingTimer(100)        # Accelerations-læsnings objekt
gps_timer = NonBlockingTimer(1000)       # GPS positionerings objekt
temp_timer = NonBlockingTimer(1000)      # Temperatur målings objekt
battery_timer = NonBlockingTimer(2500)  # Batteri procent målings objekt
esp_timer = NonBlockingTimer(100)

uart = UART(gps_port, gps_speed)         # UART object creation
gps = GPS_SIMPLE(uart)                   # GPS object creation

i2c = I2C(0)    

client = TBDeviceMqttClient(secret.SERVER_IP_ADDRESS, access_token = secret.ACCESS_TOKEN)

# Metode til temperaturlæsning, plus print i konsollen
def temp_reading():
    
    imu_data = mpu6050.get_values()
    temp1 = {"temperature_celsius": imu_data["temperature celsius"]}

    # Hent værdien ud af ordbogen
    temp_value = int(temp1["temperature_celsius"])

    # Printer temperatur på LCD
    lcd.move_to(0, 0)
    lcd.putstr(f'Temp: {temp_value}C')

# Metode til GPS-Kordinater og hastighed, plus print i konsollen
def cords_speed():
    if gps.receive_nmea_data():
        
        # Henter og printer LAT/LON/COURSE/SPEED til LCD
        lcd.move_to(0, 1)
        lcd.putstr(f'X:{gps.get_latitude()}Y:{gps.get_longitude()}')
        lcd.move_to(0, 2)
        lcd.putstr(f'{int(gps.get_speed())} KM/T')
        lcd.move_to(7,2)
        lcd.putstr(f'Course: {gps.get_course()}')
        
        # Sender information om LAT/LON/COURSE/SPEED til Thingsboard
        gps_telemetry = {
        "latitude": gps.get_latitude(),
        "longitude": gps.get_longitude(),
        "speed": int(gps.get_speed())
        }
        client.send_telemetry(gps_telemetry)

# Metode til visning af batteri-procent
def battery():

    # Omdannere ADC værdi til et procent-tal
    val = battery_adc.read_adc()
    battery_percent = int(bat_perc.batt_percentage(bat_perc.batt_voltage(val)))
    
    # Opdaterer batteri-procent på LCD
    lcd.custom_char(0, batteri_char)
    lcd.move_to(16, 0)
    lcd.putstr(f"{str(int(battery_percent))}%")
    lcd.move_to(19, 0)
    lcd.putchar(chr(0))

    # Sender information om batteriet til Thingsboard
    battery_telemetry = {
    "battery_percentage": int(battery_percent)
    }
    client.send_telemetry(battery_telemetry)
    

# Forbinder til Thingsboard
client.connect()

# Hovedloop
while True:
    # Temperatur læsning med en non-blocking timer
    temp_timer.non_blocking_timer(temp_reading)

    # Koordinat og hastighedslæsning med en non-blocking timer
    gps_timer.non_blocking_timer(cords_speed)

    # Batteri-procent med en non-blocking timer
    battery_timer.non_blocking_timer(battery)

    # Advarselsystem til blindvinkel-sensorer
    lcd_warning.lcd_warnings(right, left)