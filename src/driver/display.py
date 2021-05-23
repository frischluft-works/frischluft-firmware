# Early 2021
# Author overflo
# Part of frischluft.works
# Filename: display.py
# Purpose: Handles the SSD1606 display on I2C bus
# License Details found @ /LICENSE file in this repository


from machine import Pin, I2C
from lib import ssd1306
import time
import config


#import gc



# ESP32 Pin assignment
i2c = I2C(-1, scl=Pin(22), sda=Pin(21))

# ESP8266 Pin assignment
#i2c = I2C(-1, scl=Pin(5), sda=Pin(4))

pixelfont = [
    #0
    [
    [0,0,1,1,1,1,0,0], 
    [0,1,1,1,1,1,1,0], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [0,1,1,1,1,1,1,0],  
    [0,0,1,1,1,1,0,0],                            
    ],
    
    #1
    [
    [0,0,0,0,1,1,1,0], 
    [0,0,0,1,1,1,1,0], 
    [0,0,1,1,0,1,1,0], 
    [0,1,1,0,0,1,1,0], 
    [1,1,0,0,0,1,1,0], 
    [0,0,0,0,0,1,1,0], 
    [0,0,0,0,0,1,1,0], 
    [0,0,0,0,0,1,1,0], 
    [0,0,0,0,0,1,1,0], 
    [0,0,0,0,0,1,1,0], 
    [0,0,0,0,0,1,1,0], 
    [0,0,0,0,0,1,1,0], 
    [0,0,0,0,0,1,1,0], 
    [0,0,0,0,0,1,1,0], 
    ],

    #2
    [
    [0,0,0,1,1,1,0,0], 
    [0,0,1,1,1,1,1,0], 
    [0,1,1,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1],     
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,1,1,0], 
    [0,0,0,0,1,1,0,0], 
    [0,0,0,1,1,0,0,0], 
    [0,0,1,1,0,0,0,0], 
    [0,1,1,0,0,0,0,0], 
    [1,1,0,0,0,0,0,0], 
    [1,1,1,1,1,1,1,1],  
    [1,1,1,1,1,1,1,1], 
    ],

    #3
    [
    [0,0,1,1,1,1,0,0], 
    [0,1,1,1,1,1,1,0], 
    [1,1,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,1,1,0], 
    [0,0,1,1,1,1,0,0], 
    [0,0,1,1,1,1,1,0], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [0,1,1,1,1,1,1,0], 
    [0,0,1,1,1,1,0,0], 
    ],

    #4
    [
    [0,1,1,0,0,0,1,1], 
    [0,1,1,0,0,0,1,1], 
    [0,1,1,0,0,0,1,1], 
    [0,1,1,0,0,0,1,1], 
    [0,1,1,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1],
    [1,1,0,0,0,0,1,1], 
    [1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    ],

    #5
    [
    [1,1,1,1,1,1,1,1], 
    [1,1,1,1,1,1,1,1], 
    [1,1,0,0,0,0,0,0], 
    [1,1,0,0,0,0,0,0], 
    [1,1,0,0,0,0,0,0], 
    [1,1,1,1,1,1,0,0], 
    [0,1,1,1,1,1,1,0], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    [1,1,1,1,1,1,1,0], 
    [0,1,1,1,1,1,0,0], 
    ],

    #6
    [
    [0,0,1,1,1,1,1,0], 
    [0,1,1,1,1,1,1,1], 
    [1,1,0,0,0,0,0,0], 
    [1,1,0,0,0,0,0,0], 
    [1,1,0,0,0,0,0,0], 
    [1,1,0,0,0,0,0,0],     
    [1,1,1,1,1,1,0,0], 
    [1,1,1,1,1,1,1,0], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [0,1,1,1,1,1,1,0], 
    [0,0,1,1,1,1,0,0], 
    ],

    #7
    [
    [1,1,1,1,1,1,1,1], 
    [1,1,1,1,1,1,1,1],    
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,1,1,0], 
    [0,0,0,0,0,1,1,0], 
    [0,0,0,0,1,1,0,0], 
    [0,0,0,0,1,1,0,0], 
    [0,0,0,1,1,0,0,0], 
    [0,0,0,1,1,0,0,0], 
    [0,0,1,1,0,0,0,0], 
    [0,0,1,1,0,0,0,0], 
    [0,1,1,0,0,0,0,0], 
    [0,1,1,0,0,0,0,0], 
    ],

    #8
    [
    [0,0,1,1,1,1,0,0], 
    [0,1,1,1,1,1,1,0], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [0,1,1,0,0,1,1,0], 
    [0,0,1,1,1,1,0,0], 
    [0,1,1,1,1,1,1,0], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [0,1,1,1,1,1,1,0], 
    [0,0,1,1,1,1,0,0], 
    ],

    #9
    [
    [0,0,1,1,1,1,0,0], 
    [0,1,1,1,1,1,1,0], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [0,1,1,1,1,1,1,1], 
    [0,0,1,1,1,1,1,1], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    [0,0,0,0,0,0,1,1], 
    [1,1,0,0,0,0,1,1], 
    [0,1,1,1,1,1,1,0], 
    [0,0,1,1,1,1,0,0], 
    ],




    ]



class Display:
    def __init__(self):
        oled_width = 128
        oled_height = 64
        available=False
        try:
            self.oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
            self.available = True
        except Exception as e:
            print("Display can not be initalized :( -> ", e)
            self.available=False

        # we might rotate the display with something like this..
        #self.oled.write_cmd(ssd1306.SET_COM_OUT_DIR | 0x01)
        #self.oled.write_cmd(ssd1306.SET_SEG_REMAP | 0x01)




    def nicefont(self,number,offset):

        #print("nicefont called for number %i @ %i" % (number,offset))
        rcounter=2
        for row in pixelfont[number]:
            pcounter=0
            for pxl in row:
                #print(pxl)
                #print("x %i y %i pxl %i"% (offset+pcounter,rcounter,pxl))
                self.oled.pixel(offset+pcounter,rcounter,pxl)
                pcounter+=1
            rcounter+=1
            #print(gc.mem_free())


    def  paint_messwert(self,ppm):
        #ppm=1908
        if self.available == False:
            print("returning in paint_messwert")
            return 

        #print("display.paint_messwert -> " +str(ppm)) 
        #self.flush()

        # irgendwas hier hunzt und das display crasht MANCHMAL.
        # font scheint OK
        # memory passt vermutlich auch
        # manchmal gibts einen bytearray index out in der exception im main loop
        # das kommt VERMUTLICH vom sensor.

        #clear painting area
        for x in range(320):
            for y in range(16):
                self.oled.pixel(x,y,0)


        count = str(ppm)
        for n in range(len(count)):
            i = int(count[n])
            #self.nicefont(i,(n*10))
            self.nicefont(i,40+(n*15))
        
        #derweil:
        self.oled.text("ppm", 98,8)

        

        #print(gc.mem_free()





        #self.oled.text("Aktueller PPM", 10, 18) # ab zeile 16 blau bis dahin gelb
        #self.oled.invert()

        #self.oled.show()
        pass

    def show_config_erase(self):
        if not self.available:
            return        
        self.flush()
        self.paint_text("RESETTING CONFIG", 0, 2)
        self.oled.show()
        for i in range(3):
            self.paint_text(".", i*3, 15)
            time.sleep(1)
            self.oled.show()
        self.flush()
        self.oled.show()

    def show_info(self):
        if not self.available:
            return        
        self.flush()
        self.paint_text("DEVICE ID:", 0, 2)
        for i in range(0,6):
            self.paint_text(config.MACHINE_ID.upper()[(i*2)], 3+(i*19), 18)
            self.paint_text(config.MACHINE_ID.upper()[(i*2)+1], 11+(i*19), 18)

        self.paint_text("FW ID:", 0, 40)
        self.paint_text(config.SOFTWARE_VERSION, 50, 40)
        self.oled.show()



    def show_restart(self):
        if not self.available:
            return  
        self.flush()
        self.paint_text("frischluft.works", 0, 2)
        self.paint_text("NEUSTART", 0, 20)
        self.oled.show()

    def show_calibration(self):
        if not self.available:
            return  
        self.flush()
        self.paint_text("KALIBRIEREN", 20, 0)
        self.paint_text("Bitte lege das", 5, 16)
        self.paint_text("Geraet fuer 20", 5, 25)           
        self.paint_text("Minuten an ein", 5, 34)
        self.paint_text("geoeffnetes", 5, 43)  
        self.paint_text("Fenster", 5, 53) 
        self.oled.show()    


    def show_hello(self):
        if not self.available:
            return
        self.flush()
        self.paint_text("frischluft.works", 0, 5)
        self.oled.show()
        pass


    def paint_text(self,text,x,y):
        if not self.available:
            return
        #print("display.show_messwert -> " +str(ppm))
        #self.flush()
        self.oled.text(str(text), x, y)
        #self.oled.text("MQTT connecting", 5, 25)
        self.show()
        pass

    def show(self):
        if not self.available:
        #    print("DISPLAY NOT AVAILABLE?")
            return    
        #print("display.show()")
        self.oled.show()
        pass

    def flush(self):
        if not self.available:
            return
        self.oled.fill(0)
        pass



