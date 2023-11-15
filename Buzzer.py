# NTDEV - ID: 012
# VERSION: ALPHA 0.1

# Imports
import time
import RPi.GPIO as GPIO

# Class
class buzzer_controller():
    def __init__(self, pin):
        self._pin = pin
        self._isactive = True
        self._GPIO_init()

    def _GPIO_init(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup (self._pin, GPIO.OUT)

    def activate(self):
        self._isactive = True

    def deactivate(self):
        self._isactive = False

    def continuous_buzz(self, state):
        if not self._isactive:
            return
        if state:
            GPIO.output(self._pin, GPIO.HIGH)
        else:
            GPIO.output(self._pin, GPIO.LOW)
    
    def beep_nonstop(self, beep_time: int = 1):
        if not self._isactive:
            return
        count_time = 0
        while beep_time != count_time:
            GPIO.output(self._pin, GPIO.HIGH)
            time.sleep(.25)
            GPIO.output(self._pin, GPIO.LOW)
            time.sleep(.25)
            count_time += .5

    def single_beep(self):
        if not self._isactive:
            return
        GPIO.output(self._pin, GPIO.HIGH)
        time.sleep(.1)
        GPIO.output(self._pin, GPIO.LOW)
    
    def notify_beep(self):
        if not self._isactive:
            return
        for _ in range(3):
            GPIO.output(self._pin, GPIO.HIGH)
            time.sleep(.1)
            GPIO.output(self._pin, GPIO.LOW)
            time.sleep(.1)

    def error_beep(self):
        if not self._isactive:
            return
        for _ in range(3):
            GPIO.output(self._pin, GPIO.HIGH)
            time.sleep(2)
            GPIO.output(self._pin, GPIO.LOW)
            time.sleep(.1)
    
    def continuous_error_beep(self):
        if not self._isactive:
            return
        while True:
            GPIO.output(self._pin, GPIO.HIGH)
            time.sleep(2)
            GPIO.output(self._pin, GPIO.LOW)
            time.sleep(.2)
            GPIO.output(self._pin, GPIO.HIGH)
            time.sleep(.2)
            GPIO.output(self._pin, GPIO.LOW)
            time.sleep(1)
    
    def GPIO_clearout(self):
        self.notify_beep()
        GPIO.output(self._pin, GPIO.LOW)
        GPIO.cleanup()