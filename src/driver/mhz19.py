# Early 2021
# Author overflo
# Part of frischluft.works
# Filename: mhz19.py
# Purpose: Handles communication with the MH-Z19(b,C) Sensor
# License Details found @ /LICENSE file in this repository



from machine import UART
import time
import config

class mhz19:
    def __init__(self):
        self.ppm = 0
        self.temp= 0
        self.co2status =0
        self.warm = False
        self.available = False
        self.start()

    def start(self):
        if (config.HARDWARE_CONFIGURATION == 2):
            print("MHZ19 on UART1 WROVER-32")
            self.uart = UART(1, tx=2, rx=15, baudrate=9600)
            self.available=True
        else:
            print("MHZ19 on UART2 DEVBOARD pinout")
            self.uart = UART(2, baudrate=9600)
            print(" UART(2, baudrate=9600)")
            self.available=True

        if(self.available):
            self.uart.init(9600, bits=8, parity=None, stop=1, timeout=10)
            #print("self.available =True")

    def stop(self):
        while self.uart.any():
            self.uart.read(1)
        self.uart.deinit()

    def calibrate(self):
        print("Calibrating sensor")
        #self.uart.write(b"\xff\x01\x87\x00\x00\x00\x00\x00\x79")
        self.uart.write(b"\xff\x01\x87\x00\x00\x00\x00\x00")


    def get_data(self):

        #print("sensor.get_data(step 1) ->")
        #print(self.available)

        if not self.available:
            return 0
   
        #print("sensor.get_data( step 2)")

        self.uart.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")
        # self.uart.write(b"\xff\x01\x86\x00\x00\x00\x00\x00")
        time.sleep(0.1)
        s = self.uart.read(9)
        try:
            z=bytearray(s)
        except:
            print("wtf - garbage on UART :(")
            return 0

        # Calculate crc
        crc=self.crc8(s)
        if crc != z[8]:
            self.stop()
            time.sleep(1)
            self.start()

            print('CRC error calculated %d bytes= %d:%d:%d:%d:%d:%d:%d:%d crc= %dn' % (crc, z[0],z[1],z[2],z[3],z[4],z[5],z[6],z[7],z[8]))
            return 0
        else:
            self.ppm = ord(chr(s[2])) *256 + ord(chr(s[3]))

            #print("PPM set")

            # not initalized yet
            if self.ppm == 410 and self.warm == False:
                print("not warm 410")
                return 0
                
            self.warm = True
            self.temp = ord(chr(s[4])) -40
            self.co2status = ord(chr(s[5]))
            #testing
            self.co2status=2000
            return 1

    def crc8(self, packet):
        if len(packet) != 9:
            # Return impossible checksum on packet length error
            return 256

        crc = 0x00
        for i in range(1, 8):
            # Sum bytes 1 through 7, ignore 0 (always 255) and 8 (device CRC)
            crc += packet[i]
        crc = 0xff - (crc % 256)
        return (crc + 1) % 256
