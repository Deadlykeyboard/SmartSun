import sys
import time
import RPi.GPIO as GPIO

class StepperDomainError(Exception):
    pass

class StepperExecutionError(Exception):
    pass


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
        while self._step != 0:
            self._make_step('cww')

    def goto_specified(self, angle):
        '''
        TODO: Stepper ccw, na middendag.
        TODO: Select by smallest route.
        progress bar stepper??
        '''
        
        if self._which == 'STY': domain = [0, 90]
        elif self._which == 'STX': domain = [0, 360]

        current_angle = self.get_angle()
        print(f"""INCOMMING DATA:
Selected_stepper: {self._which}
Requested_angle: {angle}
Current_angle: {self.get_angle()}
Requested_steps: {self.get_step(angle) - self._step}""")

        try:
            if ((domain[0] <= angle) and (angle <= domain[1])):
                requested_steps = self.get_step(angle) - self._step
                
                for _ in range(requested_steps):
                    self._make_step('cw')

            else:
                raise StepperDomainError("StepperDomainError: The value specified is not in the domain supported by this machine.")
        
        except StepperExecutionError as e:
            print("StepperExecutionError: The has been some trouble processing the given data.")


    def get_step(self, angle: float) -> int:
        return int(((self._steps/360) * angle))

    def get_angle(self) -> float:
        return (360/self._steps) * self._step # calculate angle


    def _make_step(self, dir: str = 'cw') -> bool:
        def check_domain():
            if self._step > 4095: self._step = 0
            elif self._step < 0: self._step = 4095

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

        except:
            return False
            exit()


# x_stepper = stepper_controller(pins=PINS_X_STEPPER, steps=4096)
# y_stepper = stepper_controller(pins=PINS_Y_STEPPER, steps=4096)

