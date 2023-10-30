# NTDEV - ID: 012
# VERSION: ALPHA 0.1

# Imports
import base64
import os
import time
import argparse

from Display import display_controller
from SmartSunPos import SmartSunPos
from SmartSun_GPIO_Controller import stepper_controller, StepperDomainError, StepperExecutionError
from Buzzer import buzzer_controller

# Setup
PINS_X_STEPPER = (17, 27, 22, 23)
PINS_Y_STEPPER = (24, 5, 6, 16)
BUZZER_PIN = (25)
_termsize_ = 0

x_stepper = stepper_controller(PINS_X_STEPPER, which='STX')
y_stepper = stepper_controller(PINS_Y_STEPPER, which='STY')

disp = display_controller()
buzz = buzzer_controller(pin=BUZZER_PIN)

# Device & Software specific
_version_ = 'ALPHA-0.10'
_ntdevid_ = '012'
_device_ = 'RPI-4'
_unit_ = 'Dev unit'

# Locale settings
location = (52.09061, 5.12143)
timezone = 2

# Argument initialization
parser = argparse.ArgumentParser()
parser.add_argument("--terminal", '-t', help="Starts program in terminal mode", action='store_true')
parser.add_argument("--cron", '-c', help="Starts program in cron mode", action='store_true')
parser.add_argument("--silent", '-s', help="Starts program in silent mode", action='store_true')
args = parser.parse_args()

if args.silent:
    buzz.deactivate()

if not args.cron:
    _termsize_ = os.get_terminal_size().columns

# Boot screen
disp.cdprint("PWS - STARTUP", cline=1)
for i in range(17):
    disp.cdprint(i * '#', cline=2, center=False)
    buzz.single_beep()

time.sleep(3)
disp.cdprint(str(base64.b64decode('KEMpIE5pZWssIFRpbW8='))[2:-1], cline=2); time.sleep(1.5)
disp.cdprint(f'NTdev id: {_ntdevid_}', cline=2); time.sleep(1.5)
disp.cdprint(f'Ver: {_version_}', cline=2); time.sleep(1.5)
disp.cdprint(f'Device: {_device_}', cline=2); time.sleep(1.5)
disp.cdprint(f'Unit: {_unit_}', cline=2); time.sleep(1.5)

buzz.continuous_buzz(True)
if not args.silent: time.sleep(2)
buzz.continuous_buzz(False)
if not args.silent: time.sleep(.5)
buzz.single_beep()


# Stepper system
def update_steppers(x_angle: float, y_angle: float) -> bool:
    if not (y_angle <= 0):

        # Elevation
        y_angle = (90 - y_angle)
        try:
            buzz.notify_beep()
            disp.cdprint("Adjusting Y...", cline= 1)
            disp.cdprint("Please wait...", cline= 2)
            y_stepper.goto_specified(y_angle)
            time.sleep(1)
        except StepperDomainError:
            disp.dprint("ERROR Ref No. 3")
            print('An error has occured STY')
            buzz.error_beep(2)
            time.sleep(2)
            pass
        
        # Azimuth
        try:
            buzz.notify_beep()
            disp.cdprint("Adjusting X...", cline= 1)
            disp.cdprint("Please wait...", cline= 2)
            x_stepper.goto_specified(x_angle)
            time.sleep(1)
            return True
        except StepperDomainError:
            disp.dprint("ERROR Ref. No. 2")
            print('An error has occured STX')
            buzz.error_beep()
            time.sleep(2)
            pass
    
        # If the sun's under, elev < 0
    else:
        try:
            buzz.beep_nonstop(5)
            disp.cdprint("Sun's under...", cline=1)
            disp.cdprint("Retmsg 2 stepper", cline=2); time.sleep(1)
            x_stepper.return_default()
            y_stepper.return_default()
            disp.cdprint("Device standby..", cline=2)
            time.sleep(1800) # check up with an interval of half an hour 60 * 30 = 1800
        except:
            disp.dprint("ERROR Ref. No. 1")
            print("An error has occured while returning or after returning for sleep mode.")
            buzz.error_beep()
            time.sleep(2)
            pass

_man_time = (2023, 0, 0, 0, 0, 0, 0)
_sys_time = True

# Mainloop
while True:
    try:
        # in call ssp: man_time=(y, m, d, h, m, s, timezone)       
        obj = SmartSunPos(use_system_time=_sys_time, man_time=_man_time, return_time=True, location=location, timezone=timezone, refraction=True)
        azimuth, elevation, time_of_measurement = obj.sun_position
            
        #---DESKTOP---#
        if args.terminal:
            print("-" * _termsize_)
            print(f"Last measurement: {obj.data}")
            print(f"Current azimuth: {azimuth} degrees\nCurrent elevation: {elevation} degrees")
            print("-" * _termsize_)
            time.sleep(1)

        #---PI---#
        disp.cdprint(f"AZIM: {azimuth}", cline=1)
        disp.cdprint(f"ELEV: {elevation}", cline=2)
        time.sleep(1)
        update_steppers(x_angle=azimuth, y_angle=elevation)
        disp.dprint(f"LastMeasurement:{time_of_measurement[0]}/{time_of_measurement[1]}/{time_of_measurement[2]}/{time_of_measurement[3]}/{time_of_measurement[4]}")
        buzz.single_beep()
        time.sleep(30)

    except KeyboardInterrupt:
        disp.turn_off()
        buzz.GPIO_clearout()

        x_stepper.GPIO_clearout()
        y_stepper.GPIO_clearout()
        exit()