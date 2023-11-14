# NTDEV - ID: 012
# VERSION: ALPHA 0.1


import RPi.GPIO as GPIO
import time

class LightController():
    def __init__(self, pin):
        self._pin = pin
        self._GPIO_setup()
    
    def GPIO_clearout(self) -> None:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.IN)
        GPIO.setup(self._pin, GPIO.LOW)
        GPIO.cleanup()
    
    def _GPIO_setup(self) -> None:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup (self._pin, GPIO.OUT)
        GPIO.output(self._pin, GPIO.LOW)
    
    def blink(self):
        while True:
            GPIO.output(self._pin, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(self._pin, GPIO.LOW)
            time.sleep(1)
    
    def turn_on(self):
        GPIO.output(self._pin, GPIO.HIGH)
        return
    
    def turn_off(self):
        GPIO.output(self._pin, GPIO.LOW)
        return
