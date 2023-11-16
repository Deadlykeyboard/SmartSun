# NTDEV - ID: 012
# VERSION: ALPHA 0.1

# Imports
import base64
import os
import time
import argparse
import threading

from LightController import LightController
from Misc import GPIO_utils as gu
from Misc import NTPtime
from Misc import EthernetInfo
from Display import display_controller
from SmartSunPos import SmartSunPos
from SmartSun_GPIO_Controller import stepper_controller, StepperDomainError, StepperExecutionError
from Buzzer import buzzer_controller
# Setup
PINS_X_STEPPER = (17, 27, 22, 23)
PINS_Y_STEPPER = (24, 5, 6, 16)
BUZZER_PIN = (25)
ERROR_LIGHT_PIN = (26)
_termsize_ = 0

disp = display_controller()
buzz = buzzer_controller(pin=BUZZER_PIN)
error_light = LightController(pin=ERROR_LIGHT_PIN)
ether = EthernetInfo()

ADJUST_PERPENDICULAR_ANGLE = True

# pre-start check
while not ether.CheckInternetAvailability():
    buzz.single_beep()
    disp.cdprint('Waiting for:', cline=1)
    disp.cdprint('Internet', cline=2)
    time.sleep(1)

disp.dprint('OK')
time.sleep(1)

x_stepper = stepper_controller(PINS_X_STEPPER, which='STX')
y_stepper = stepper_controller(PINS_Y_STEPPER, which='STY')

if ether.CheckInternetAvailability():
    ntptime = NTPtime()

# Device & Software specific
_version_ = 'ALPHA-0.10'
_ntdevid_ = '012'
_device_ = 'RPI-4'
_unit_ = 'Dev unit'
_ip_ = ether.MyIP()

# Locale settings
location = (52.09061, 5.12143)
timezone = 2

# Argument initialization
parser = argparse.ArgumentParser()
parser.add_argument("--terminal", '-t', help="Starts program in terminal mode", action='store_true')
parser.add_argument("--cron", '-c', help="Starts program in cron mode", action='store_true')
parser.add_argument("--silent", '-s', help="Starts program in silent mode", action='store_true')
parser.add_argument("--fast", '-f', help="Starts in fast-start mode", action='store_true')
args = parser.parse_args()

if args.silent:
    buzz.deactivate()

if not args.cron:
    _termsize_ = os.get_terminal_size().columns

# Boot screen
disp.cdprint("STARTING", cline=1)

if not args.fast:
    for i in range(17):
        disp.cdprint(i * '#', cline=2, center=False)
        buzz.single_beep()

    time.sleep(3)
    disp.cdprint(str(base64.b64decode('KEMpIE5pZWssIFRpbW8='))[2:-1], cline=2); time.sleep(1.5)
    disp.cdprint(f'NTdev id: {_ntdevid_}', cline=2); time.sleep(1.5)
    disp.cdprint(f'Ver: {_version_}', cline=2); time.sleep(1.5)
    disp.cdprint(f'Device: {_device_}', cline=2); time.sleep(1.5)
    disp.cdprint(f'Unit: {_unit_}', cline=2); time.sleep(1.5)
    disp.cdprint(f'IP:{_ip_}', cline=2); time.sleep(1.5)

    buzz.continuous_buzz(True)
    if not args.silent: time.sleep(2)
    buzz.continuous_buzz(False)
    if not args.silent: time.sleep(.5)

buzz.single_beep()

error_blink = threading.Thread(target=error_light.blink)
error_beep = threading.Thread(target=buzz.continuous_error_beep)

def throw_physical_error():
    try:
        error_blink.start()
        error_beep.start()
        ThreadsActive = True
    except KeyboardInterrupt:
        return

    except RuntimeError:
            print("a thread error occured while starting up. (Maybe it was already running?)")



# Stepper system
def update_steppers(x_angle: float, y_angle: float):
    if not (y_angle <= 0):
        # Elevation
        y_angle = (90 - y_angle)
        try:
            buzz.notify_beep()
            disp.cdprint("Adjusting Y...", cline= 1)
            disp.cdprint("Please wait...", cline= 2)
            y_stepper.goto_specified(y_angle)
            time.sleep(1)
            return

        except KeyboardInterrupt:
            graceful_shutdown()

        except StepperDomainError:
            disp.dprint("ERROR Ref No. 3")
            print('An error has occured STY')
            throw_physical_error()
            time.sleep(2)
            return

        x_angle = (x_angle - 90) if ADJUST_PERPENDICULAR_ANGLE else x_angle
        # Azimuth
        try:
            buzz.notify_beep()
            disp.cdprint("Adjusting X...", cline= 1)
            disp.cdprint("Please wait...", cline= 2)
            x_stepper.goto_specified(x_angle)
            time.sleep(1)
            return

        except KeyboardInterrupt:
            graceful_shutdown()

        except StepperDomainError:
            disp.dprint("ERROR Ref. No. 2")
            print('An error has occured STX')
            throw_physical_error()
            time.sleep(2)
            return
    
        # If the sun's under, elev < 0
    else:
        try:
            buzz.beep_nonstop(5)
            error_light.turn_on()
            disp.cdprint("Sun's under...", cline=1)
            disp.cdprint("Retmsg 2 stepper", cline=2); time.sleep(1)
            x_stepper.return_default()
            y_stepper.return_default()
            disp.cdprint("Device standby..", cline=2)
            time.sleep(1800) # check up with an interval of half an hour 60 * 30 = 1800
            return

        except KeyboardInterrupt:
            graceful_shutdown()

        except:
            disp.dprint("ERROR Ref. No. 1")
            print("An error has occured while returning or after returning for sleep mode.")
            throw_physical_error()
            time.sleep(2)
            return
        
        


def graceful_shutdown():
    try:
        print("\n[SHUTDOWN] Starting Process")    
        try:
            print("[SHUTDOWN] Stopping threads")
            error_blink.join()
            error_beep.join()
        
        except Exception:
            pass
            
        try:
            print("[SHUTDOWN] Cleaning up GPIO module ")
            disp.turn_off()
            buzz.GPIO_clearout()
            error_light.GPIO_clearout()
            x_stepper.GPIO_clearout()
            y_stepper.GPIO_clearout()
            p = gu()
            p.global_clearout() # eig compleet NIET nodig...
        
        except Exception:
            pass
    
    except Exception as e:
        print(f"The 'graceful-shutdown-function' encountered a error:\n{e}")

    finally:
        print("[SHUTDOWN] Exitting...")
        exit()


_sys_time = False # System time often not set correctly.
_adjust_timezone = False if ntptime.DST_in_effect else True
_time_by_ntp_ = ntptime.FormattedNTPTime()
_man_time = _time_by_ntp_ #(2023, 0, 0, 0, 0, 0, 0)
timezone += 1 if _adjust_timezone else timezone
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
        graceful_shutdown()