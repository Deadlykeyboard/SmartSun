# Imports
import base64
import os
import time
import argparse

from Display import display_controller
from SmartSunPos import SmartSunPos
from SmartSun_GPIO_Controller import stepper_controller, StepperDomainError, StepperExecutionError

PINS_X_STEPPER = (17, 27, 22, 23)
PINS_Y_STEPPER = (24, 5, 6, 16)

_version_ = 'BETA V0.1'
_ntdevid_ = '012'
disp = display_controller()

parser = argparse.ArgumentParser()
parser.add_argument("--terminal", '-t', help="Starts also the terminal variant", action='store_true')
parser.add_argument("--cron", '-c', help="Starts program in cron mode", action='store_true')
args = parser.parse_args()

if not args.cron:
    _termsize_ = os.get_terminal_size().columns


# Boot screen
disp.cdprint("PWS - STARTUP", cline=1)
for i in range(17):
    disp.cdprint(i * '#', cline=2, center=False)
    time.sleep(.1)
time.sleep(3)
disp.cdprint(str(base64.b64decode('KEMpIE5pZWssIFRpbW8='))[2:-1], cline=2)
time.sleep(1)
disp.cdprint(f'ntdev id: {_ntdevid_}', cline=2)
time.sleep(1)
disp.cdprint(_version_, cline=2)
time.sleep(2)

# Locale settings
location = (52.09061, 5.12143)
timezone = 2

x_stepper = stepper_controller(PINS_X_STEPPER, which='STX')     # AZI = 0* = middennacht, zon andere kant noord. # AZI = 180* = mid dag, zon onze kant zuid.
y_stepper = stepper_controller(PINS_Y_STEPPER, which='STY')     # LEV = 90* = zonnepaneel recht omhoog. [DOMEIN=0, 90] (hij kan wel de andere kant op maar hoeft niet)


# Stepper system
def update_steppers(x_angle: float, y_angle: float) -> bool:
    if not (y_angle <= 0):
    #print(x_angle, y_angle)
        y_angle = (90 - y_angle)
        try:
            disp.cdprint("Adjusting Y...", cline= 1)
            disp.cdprint("Please wait...", cline= 2)
            y_stepper.goto_specified(y_angle)
            time.sleep(1)
        except StepperDomainError:
            disp.dprint("ERROR")
            print('An error has occured Y')
            pass
        try:
            disp.cdprint("Adjusting X...", cline= 1)
            disp.cdprint("Please wait...", cline= 2)
            x_stepper.goto_specified(x_angle)
            time.sleep(1)
            return True
        except StepperDomainError:
            disp.dprint("ERROR")
            print('An error has occured X')
            pass
    else:
        try:
            disp.cdprint("Sun's under...", cline=1)
            disp.cdprint("Retmsg 2 stepper", cline=2)
            x_stepper.return_default()
            y_stepper.return_default()
            time.sleep(5)
        except:
            disp.dprint("ERROR")
            print("An error has occured while returning...")
            pass

# Mainloop
while True:
    try:
        # in call ssp: man_time=(y, m, d, o, m, s, timezone), #man_time=(2023, 10, 24, 12, 0, 0, 2)
        obj = SmartSunPos(use_system_time=True, return_time=True, location=location, timezone=timezone, refraction=True)
        azimuth, elevation, time_of_measurement = obj.sun_position
            
        #---DESKTOP---#
        if args.terminal:
            print("-" * _termsize_)
            print(f"Last measurement: {obj.data}")
            print(f"Current azimuth: {azimuth} degrees\nCurrent elevation: {elevation} degrees")
            print("-" * _termsize_)
            time.sleep(1)

        #---PI---#
        disp.cdprint(f"Azim: {azimuth}", 1)
        disp.cdprint(f"Elev: {elevation}", 2)
        time.sleep(1)
        update_steppers(x_angle=azimuth, y_angle=elevation)
        disp.dprint(f"LastMeasurement:{time_of_measurement[0]}/{time_of_measurement[1]}/{time_of_measurement[2]}/{time_of_measurement[3]}/{time_of_measurement[4]}")
        time.sleep(20)

    except KeyboardInterrupt:
        disp.turn_off()
        
        x_stepper.GPIO_clearout()
        y_stepper.GPIO_clearout()
        exit()



