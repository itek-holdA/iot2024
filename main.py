import lcd_api, lcd_warning, time, socket, secret, gc 
from machine import Pin, UART, ADC, reset, I2C       # Machine-imports
from gpio_lcd import GpioLcd                         # LCD Modul til ???
from nonblockingtimer import NonBlockingTimer        # Non blocking timer klasse
from gps_simple import GPS_SIMPLE                    # GPS
from uthingsboard.client import TBDeviceMqttClient   # Thingsboard
from battery_percentage import BatteryPercent
from adc_substitute import AdcSubstitute
from mpu6050 import MPU6050

#Variables to update via HTTP
left = 0
right = 0
rear = 0



# GPS Variabler
gps_port = 2                                 
gps_speed = 9600                             

batteri_char = bytearray([0b01110, 0b10001, 0b10001, 0b11001, 0b11101, 0b11111, 0b11111, 0b11111])

temp1 = 0

# Objekter
lcd = GpioLcd(rs_pin=Pin(27),            # Educaboard LCD-skærm objekt
              enable_pin=Pin(25),
              d4_pin=Pin(33),
              d5_pin=Pin(32),
              d6_pin=Pin(21),
              d7_pin=Pin(22),
              num_lines=4,
              num_columns=20)

acc_timer = NonBlockingTimer(1000)        # Accelerations-læsnings objekt
gps_timer = NonBlockingTimer(1000)       # GPS positionerings objekt
temp_timer = NonBlockingTimer(1000)      # Temperatur målings objekt
battery_timer = NonBlockingTimer(5000)   # Batteri procent målings objekt
#esp_timer = NonBlockingTimer(100)
movement_timer = NonBlockingTimer(1000)
gc_timer = NonBlockingTimer(5000)


uart = UART(gps_port, gps_speed)         # UART object creation
gps = GPS_SIMPLE(uart)                   # GPS object creation

i2c = I2C(0)                             # I2C Objekt
mpu6050 = MPU6050(i2c)                   # MPU6050 Objekt med I2C-0

bat_perc = BatteryPercent()
battery_adc = AdcSubstitute(36)

client = TBDeviceMqttClient(secret.SERVER_IP_ADDRESS, access_token = secret.ACCESS_TOKEN)




# Metode til temperaturlæsning, plus print i konsollen
def temp_reading():
    
    imu_data = mpu6050.get_values()
    temp1 = {"temperature_celsius": imu_data["temperature celsius"]}

    # Hent værdien ud af ordbogen
    temp_value = int(temp1["temperature_celsius"])  # Henter tallet og konverterer til heltal

    # Printer temperatur på LCD
    lcd.move_to(0, 0)
    lcd.putstr(f'Temp: {temp_value}C       ')
    #lcd.move_to(0, 3)
    #lcd.putstr(f'                    ')
    
    temperature_telemetry = {"temp_value": int(temp_value)}
    client.send_telemetry(temperature_telemetry)

# Metode til GPS-Kordinater og hastighed, plus print i konsollen
def cords_speed():
    
    if gps.receive_nmea_data():
        
        # Henter og printer LAT/LON/COURSE/SPEED til LCD
        lcd.move_to(0, 1)
        lcd.putstr(f'X:{gps.get_latitude()}Y:{gps.get_longitude()}')
        lcd.move_to(0, 3)
        lcd.putstr(f'{int(gps.get_speed())} KM/T')
        lcd.move_to(0,2)
        lcd.putstr(f'Course: {gps.get_course()}')
        
        # Sender information om LAT/LON/COURSE/SPEED til Thingsboard
        gps_telemetry = {
        "latitude": gps.get_latitude(),
        "longitude": gps.get_longitude(),
        "speed": int(gps.get_speed()),
        "course": gps.get_course()
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
    battery_telemetry = {"battery_percentage": int(battery_percent)}
    client.send_telemetry(battery_telemetry)

def gc1():
    
    print(f"free memory: {gc.mem_free()}") # monitor memory left
    
    if gc.mem_free() < 15000:          # free memory if below 2000 bytes left
        print("Garbage collected!")
        gc.collect()                  # free memory  

# Metode til at starte HTTP-server
def start_http_server():
    
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    try:
        server = socket.socket()
        server.bind(addr)
        server.listen(1)
        print("HTTP server running on", addr)
        return server
    except OSError as e:
        print("Error starting server:", e)
        server.close()
        raise

# Metode til HTTP-requests
def handle_http_requests(server):
    global left, right, rear
    client, addr = server.accept()
    print("Client connected from:", addr)
    request = client.recv(1024).decode()
    print("Request received:", request)

    # Håndtering af variabel opdateringer
    if "POST /set_left" in request:              # Opdaterer left-variabel
        left = process_variable_update(request)
        response = f"HTTP/1.1 200 OK\r\n\r\nLeft updated to {left}!"
    elif "POST /set_right" in request:           # Opdaterer right-variabel
        right = process_variable_update(request)
        response = f"HTTP/1.1 200 OK\r\n\r\nRight updated to {right}!"
    elif "POST /set_rear" in request:            # Opdaterer rear-variabel
        rear = process_variable_update(request)
        response = f"HTTP/1.1 200 OK\r\n\r\nRear updated to {rear}!"

    client.send(response)
    client.close()

def process_variable_update(request):
    """Extract and return the variable value from the HTTP request body."""
    try:
        body_start = request.find("\r\n\r\n") + 4
        body = request[body_start:].strip()
        return int(body)
    except ValueError:
        print("Invalid value received!")
        return 0
    
timer = 0  # Ensure global timer is initialized
in_movement = 1

def movement_detection():
    global timer
    global in_movement
    speed = int(gps.get_speed())
    print(speed)
    
    if speed > 1:
        timer = 0
        print(f"Timer reset: {timer}")
        in_movement = 1
        movement_telemetry = {"in_movement": int(in_movement)}
        client.send_telemetry(movement_telemetry)
        lcd.move_to(7, 3)
        lcd.putstr(f'{timer}S')
    elif speed == 0:
        timer += 1
        print("Stand still")
        print(f"Timer incremented: {timer}")
        lcd.move_to(16, 3)
        lcd.putstr(f'{timer}S')
    if timer > 180 and speed < 1:
        print("Locked")
        in_movement = 0
        lcd.move_to(15, 3)
        lcd.putstr(f'Locked')
        movement_telemetry = {"in_movement": int(in_movement)}
        client.send_telemetry(movement_telemetry)
        
        


# Forbinder til Thingsboard
client.connect()

# Starter HTTP-server
http_server = start_http_server()

# Hovedloop
while True:
    # Temperatur læsning med en non-blocking timer
    temp_timer.non_blocking_timer(temp_reading)

    # Koordinat og hastighedslæsning med en non-blocking timer
    gps_timer.non_blocking_timer(cords_speed)

    # Batteri-procent med en non-blocking timer
    battery_timer.non_blocking_timer(battery)

    # Advarselsystem til blindvinkel-sensorer
    lcd_warning.lcd_warnings(right, left, rear)
    
    movement_timer.non_blocking_timer(movement_detection)

    # Handle incoming HTTP requests
    #handle_http_requests(http_server)
    
    gc_timer.non_blocking_timer(gc1)