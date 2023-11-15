# NTDEV - ID: 012
# VERSION: ALPHA 0.1

import socket
import time
import struct
import RPi.GPIO as GPIO

class EthernetInfo():
    def __init__(self):
        pass

    def CheckInternetAvailability(self) -> bool:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            return True
        
        except OSError:
            return False
    
    def MyIP(self) -> str:
        socket_instance = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_instance.connect(("8.8.8.8", 80))
        local_ip_address = socket_instance.getsockname()[0]
        socket_instance.close
        return local_ip_address



class NTPtime():
    def __init__(self, timeserver: str = "pool.ntp.org"):
        self._timeserver = timeserver
        self.CurrentFormattedTime = self._FormattedNTPTime()
        
    def getTimeFromServer(self):
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.settimeout(5)
        
            try:
                serveraddress = socket.gethostbyname(self._timeserver)
                ntp_req = bytearray(48)
                ntp_req[0] = 0x1B

                client.sendto(bytes(ntp_req), (serveraddress, 123))
                ntp_response, server = client.recvfrom(48)
                unpacked_response = struct.unpack("!12I", ntp_response)
                seconds_since_1900 = unpacked_response[10] - 2208988800
                return seconds_since_1900
            
            except Exception as e:
                return f"Error: {e}"
            
            finally:
                client.close()
        


    def _FormattedNTPTime(self) -> tuple:
        time_struct = time.localtime(self.getTimeFromServer())
        year, month, day, hour, minute, second = time_struct[:6]

        dst_in_effect = True if time_struct.tm_isdst == 0 else False
        timezone_offset = time.timezone if not dst_in_effect else time.altzone
        timezone_hours = abs(timezone_offset) // 3600
        timezone_sign = '-' if timezone_offset > 0 else '+'

        return year, month, day, hour, minute, second, int(f"{timezone_sign}{timezone_hours:02}")
