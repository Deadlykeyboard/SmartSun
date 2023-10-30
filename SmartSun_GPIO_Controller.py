# NTDEV - ID: 012
# VERSION: ALPHA 0.1

# Imports
import sys
import time
import RPi.GPIO as GPIO

# Exceptions
class StepperDomainError(Exception):
    pass

class StepperExecutionError(Exception):
    pass

# Class
class stepper_controller():
    def __init__(self, pins: tuple[int, int, int, int], steps: int = 4096, which: str = None):
        self._which = which # STX/STY
        self._pins = pins
        self._steps = steps
        self._step = 0   # int: 0 - 4096
        self._stepdegree = 360/self._steps
        self._phase = 0
        self._hold = self.set_desired_hold_time()
        self._seq = [
            [1, 0, 0, 1],
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1]]
            
        self._GPIO_setup()
    
    def set_desired_hold_time(self) -> float:
        return 0.005

    def GPIO_clearout(self):
        GPIO.setmode(GPIO.BCM)
        for pin in self._pins:
            GPIO.setup(pin, GPIO.IN)
            GPIO.setup(pin, GPIO.LOW)
        GPIO.cleanup()

    def _GPIO_setup(self) -> None:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        for pin in self._pins:
            print(f"setting up pin {pin}...")
            GPIO.setup (pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
            

    def return_default(self):
        self.goto_specified(0)

    def goto_specified(self, angle):
        if self._which == 'STY': domain = [0, 90]
        elif self._which == 'STX': domain = [0, 360]

        def get_closest_dir(angle):
            current_step = self._step
            goto_step = self.get_step(angle)
            a = int(goto_step - current_step)
            b = int(self._steps - (goto_step - current_step))
            if a < b:
                return 'cw'
            else:
                return 'ccw'

        try:
            if ((domain[0] <= angle) and (angle <= domain[1])):
                goto_step = self.get_step(angle)
                requested_steps_cw = int(goto_step - self._step)           
                requested_steps_ccw = int(self._steps - (goto_step - self._step))
                
                dir = get_closest_dir(angle)

                if requested_steps_cw < 0:
                    requested_steps = int(-1 * requested_steps_cw)
                    dir = 'ccw'
                    print('--Step NEG-CW--')
                elif requested_steps_ccw < 0:
                    requested_steps = int(-1 * requested_steps_ccw)
                    dir = 'cw'
                    print('--Step NEG-CCW--')
                else: 
                    if dir == 'cw': requested_steps = requested_steps_cw; print('--Step CW--')
                    else: requested_steps = requested_steps_ccw; print('--Step CCW--')
                

                print(f"""INCOMMING DATA:
Selected_stepper: {self._which}
Requested_angle: {angle}
Requested_direction: {dir}
Current_angle: {self.get_angle()}
Requested_steps: {requested_steps}\n""")
                
                for _ in range(requested_steps):
                    self._make_step(dir)

            else:
                raise StepperDomainError("StepperDomainError: The value specified is not in the domain supported by this machine.")
                exit()
        
        except StepperExecutionError as e:
            print("StepperExecutionError: The has been some trouble processing the given data.")
            exit()


    def get_step(self, angle: float) -> int:
        return int(((self._steps/360) * angle))

    def get_angle(self) -> float:
        return (360/self._steps) * self._step # calculate angle

    def _make_step(self, dir: str) -> bool:
        def check_domain():
            if self._step > (self._steps - 1): self._step = 0
            elif self._step < 0: self._step = (self._steps - 1)

        try:
            check_domain()
            match dir.lower():
                case 'cw':
                    self._phase = ((self._step + 1) % 8)
                    self._step += 1
                case 'ccw':
                    self._phase = ((self._step - 1) % 8)
                    self._step -= 1

            for pin in self._pins:
                GPIO.output(pin, self._seq[self._phase][self._pins.index(pin)])
                time.sleep(self._hold)

            return True

        except StepperExecutionError as e:
            print("StepperExecutionError: The has been some trouble processing the given data.")
            exit()