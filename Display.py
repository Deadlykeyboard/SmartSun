# NTDEV - ID: 012
# VERSION: ALPHA 1.0

# Imports
import smbus
import time

# Class
class display_controller():
    def __init__(self):
        self._I2C_ADDR = 0x27
        self._LCD_WIDTH = 16
        self._LCD_CHR = 1 # send data
        self._LCD_CMD = 0 # send command
        self._LCD_LINE_1 = 0x80 # address 1st line
        self._LCD_LINE_2 = 0xC0 # address 2nd line
        self._LCD_BACKLIGHT  = 0x08 # Backlight control bit off= 0x00, on= 0x08
        self._ENABLE = 0b00000100
        self._E_PULSE = 0.0005
        self._E_DELAY = 0.0005
        self._LCD_CLEAR = 0x01
        self._bus = smbus.SMBus(1) # Old ones = 1
        self.lcd_init()

    def turn_off(self):
        self.lcd_byte(0x01, self._LCD_CMD)
        self.lcd_byte(0x00, self._LCD_CMD)
    
    def center_string(self, string: str) -> str:
        if len(string) >= self._LCD_WIDTH:
            return string[:self._LCD_WIDTH]
        else:
            left_padding = (self._LCD_WIDTH - len(string)) // 2
            right_padding = self._LCD_WIDTH - len(string) - left_padding      
        return ' ' * left_padding + string + ' ' * right_padding


    def lcd_init(self):
        self.lcd_byte(0x33, self._LCD_CMD) # 110011 Initialise
        self.lcd_byte(0x32, self._LCD_CMD) # 110010 Initialise
        self.lcd_byte(0x06, self._LCD_CMD) # 000110 Cursor move direction
        self.lcd_byte(0x0C, self._LCD_CMD) # 001100 Display On, Cursor Off, Blink Off
        self.lcd_byte(0x28, self._LCD_CMD) # 101000 Data length, number of lines, font size
        self.lcd_byte(0x01, self._LCD_CMD) # 000001 Clear display
        time.sleep(self._E_DELAY)

    def lcd_send_command(self, command):
        # current supported commands: clear screen (CS), turn off/on backlight (CSB).
        supported_commands = {
            'CS' : lambda self: self.lcd_byte(self._LCD_CLEAR, self._LCD_CMD),
            'CSB': lambda self: self.lcd_byte(self._LCD_BACKLIGHT, self._LCD_CMD)
        }
        
        if command in supported_commands:
            function = supported_commands[command]
            function(self)


        else:
            print("UNSUPPORTED COMMAND")
            
    def lcd_byte(self, bits, mode):
        bits_high = mode | (bits & 0xF0) | self._LCD_BACKLIGHT
        bits_low  = mode | ((bits<<4) & 0xF0) | self._LCD_BACKLIGHT

        self._bus.write_byte(self._I2C_ADDR, bits_high)
        self.lcd_toggle_enable(bits_high)

        self._bus.write_byte(self._I2C_ADDR, bits_low)
        self.lcd_toggle_enable(bits_low)

    def lcd_toggle_enable(self, bits):
        time.sleep(self._E_DELAY)
        self._bus.write_byte(self._I2C_ADDR, (bits | self._ENABLE))
        time.sleep(self._E_PULSE)
        self._bus.write_byte(self._I2C_ADDR,(bits & ~self._ENABLE))
        time.sleep(self._E_DELAY)


    def lcd_string(self, message, line):
        message = message.ljust(self._LCD_WIDTH," ")
        self.lcd_byte(line, self._LCD_CMD)

        for i in range(self._LCD_WIDTH):
            self.lcd_byte(ord(message[i]),self._LCD_CHR)

    def cdprint(self, msg: str, cline: int, center: bool = True):
        if center:
            msg = self.center_string(msg)

        if cline == 1:
            self.lcd_string(msg, self._LCD_LINE_1)
        elif cline == 2:
            self.lcd_string(msg, self._LCD_LINE_2)
        else:
            print('No valid CLINE value.')


    def dprint(self, msg: str):
        dsp_list = list(msg)
        line_1 = []
        line_2 = []
        if len(dsp_list) >= 0 and len(dsp_list) <= 16:
            line_1_str = ''.join(dsp_list)
            self.lcd_string(self.center_string(line_1_str), self._LCD_LINE_1)

        elif len(dsp_list) >= 16 and len(dsp_list) <= 32:
            for i in range(16):
                line_1.append(dsp_list[i])
            for x in range(16, len(dsp_list)):
                line_2.append(dsp_list[x])

            line_1_str = ''.join(line_1)
            line_2_str = ''.join(line_2)

            self.lcd_string(self.center_string(line_1_str), self._LCD_LINE_1)
            self.lcd_string(self.center_string(line_2_str), self._LCD_LINE_2)

        else:
            print("Woh, that's to much to the good.")



