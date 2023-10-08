## Written by Deadlykeyboard
import time
import os



print("FETCHING DATA...")
for i in range(10):
    if i == 1:
        from SmartSunPos import SmartSunPos
    if i != 1:
        time.sleep(.1)
    print(f"[LOADING] {'##' * i}\033[1A")
print()

if __name__ == "__main__":
    location = (52.09061, 5.12143)
    while True:
        termsize = os.get_terminal_size().columns - 1
        obj = SmartSunPos(return_time=True, location=location, timezone=2, refraction=True)
        azimuth, elevation, time_of_measurement = obj.sun_position
        print("-" * termsize)
        print(f"Last measurement: {time_of_measurement}")
        print(f"Current azimuth: {azimuth} degrees\nCurrent elevation: {elevation} degrees")
        print("-" * termsize)
        print("\033[6A")
        time.sleep(1)