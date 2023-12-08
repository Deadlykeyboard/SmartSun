#// FILE FOR TESTING PURPOSES ONLY!

from SmartSunPos import SmartSunPos

obj = SmartSunPos(use_system_time=True, return_time=True, timezone=1)

print(obj.sun_position)
