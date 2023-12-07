#// FILE FOR TESTING PURPOSES ONLY!

from SmartSunPos import SmartSunPos

obj = SmartSunPos(use_system_time=False, man_time=(2023, 12, 7, 18, 0, 0, 0), return_time=False, timezone=1)

print(obj.sun_position)
print(obj.man_time)