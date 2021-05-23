# Early 2021
# Author overflo
# Part of frischluft.works
# Filename: aht10.py
# Purpose: Handles the AHT10 Humidity Sensor
# License Details found @ /LICENSE file in this repository


from lib.i2c_base import i2cBase
import time


class AHT10(i2cBase):

    AHT10_I2CADDR_DEFAULT = 0x38   #///< AHT10 default i2c address 
    AHT10_CMD_CALIBRATE = 0xE1     #///< Calibration command
    AHT10_CMD_TRIGGER = 0xAC       #///< Trigger reading command
    AHT10_CMD_SOFTRESET = 0xBA     #///< Soft reset command
    AHT10_STATUS_BUSY = 0x80       #///< Status bit for busy
    AHT10_STATUS_CALIBRATED = 0x08 #///< Status bit for calibrated 

    temperature=0  # in °C
    humidity=0  # in %

    active=True

    def __init__(self):
        #self.i2c = i2c
        super().__init__()
        self.addr = self.AHT10_I2CADDR_DEFAULT

        print("AHT 10 init()")

        '''
            119 bmp180   0x77
            60  ssd1306  0x3c
            98  sd41     0x62
            56  aht10    0x38
        '''

        ids = self.scan()
        if not self.addr in ids:
            print("AHT10 not found on bus")
            self.active=False
 #       else:
 #           config = bytearray([0x08, 0x00])
 #           self.writeto(0xE1, config)
 


    def update(self):
        if not self.active:
            return False

        MeasureCmd = bytearray([0x33, 0x00])
        self.writeto(0xAC, MeasureCmd)
        time.sleep(0.5)
        data = self.readfrom(0x00,6)
        #print(data)
        temp = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
        ctemp = ((temp*200) / 1048576) - 50
        #print(u'Temperature: {0:.1f}°C'.format(ctemp))
        self.temperature=round(ctemp,1)

        tmp = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
        #print(tmp)
        ctmp = int(tmp * 100 / 1048576)
        self.humidity=ctmp
        #print(u'Humidity: {0}%'.format(ctmp))        


        

