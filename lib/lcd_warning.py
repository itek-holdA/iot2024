from machine import Pin
from gpio_lcd import GpioLcd                  # LCD Modul til ???
import lcd_api                                # LCD API
import time

lcd = GpioLcd(rs_pin=Pin(27),          #Thingsboard skærm
              enable_pin=Pin(25),
              d4_pin=Pin(33),
              d5_pin=Pin(32),
              d6_pin=Pin(21),
              d7_pin=Pin(22),
              num_lines=4,
              num_columns=20)

left_arrow_char = bytearray([0b00010, 0b00110, 0b01110, 0b11110, 0b11110, 0b01110, 0b00110, 0b00010])
right_arrow_char = bytearray([0b01000, 0b01100, 0b01110, 0b01111, 0b01111, 0b01110, 0b01100, 0b01000])

def lcd_warnings(right, left):
    if left == 1 and right == 1:
        lcd.custom_char(1, left_arrow_char)
        lcd.custom_char(2, right_arrow_char)
        lcd.clear()
        lcd.move_to(4,0)
        lcd.putstr(f'Bagvedkorende')
        lcd.move_to(3,1)
        lcd.putstr(f'På begge sider')
        lcd.move_to(7,2)
        lcd.putstr(f'Pas pa!')
        lcd.move_to(0,0)
        lcd.putchar(chr(1))
        lcd.move_to(0,1)
        lcd.putchar(chr(1))
        lcd.move_to(0,2)
        lcd.putchar(chr(1))
        lcd.move_to(0,3)
        lcd.putchar(chr(1))
        lcd.move_to(19,0)
        lcd.putchar(chr(2))
        lcd.move_to(19,1)
        lcd.putchar(chr(2))
        lcd.move_to(19,2)
        lcd.putchar(chr(2))
        lcd.move_to(19,3)
        lcd.putchar(chr(2))
        time.sleep(5)
    elif left == 1 and right == 0:
        lcd.custom_char(1, left_arrow_char)
        lcd.custom_char(2, right_arrow_char)
        lcd.clear()
        lcd.move_to(4,0)
        lcd.putstr(f'Bagvedkorende')
        lcd.move_to(3,1)
        lcd.putstr(f'På venstre side')
        lcd.move_to(7,2)
        lcd.putstr(f'Pas pa!')
        lcd.move_to(0,0)
        lcd.putchar(chr(1))
        lcd.move_to(0,1)
        lcd.putchar(chr(1))
        lcd.move_to(0,2)
        lcd.putchar(chr(1))
        lcd.move_to(0,3)
        lcd.putchar(chr(1))
        time.sleep(5)
    elif right == 1 and left == 0:
        lcd.custom_char(1, left_arrow_char)
        lcd.custom_char(2, right_arrow_char)
        lcd.clear()
        lcd.move_to(1,1)
        lcd.putstr(f'Pas på hojre side')
        lcd.move_to(19,0)
        lcd.putchar(chr(2))
        lcd.move_to(19,1)
        lcd.putchar(chr(2))
        lcd.move_to(19,2)
        lcd.putchar(chr(2))
        lcd.move_to(19,3)
        lcd.putchar(chr(2))
        time.sleep(5)
    else:
        pass