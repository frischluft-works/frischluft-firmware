# Early 2021
# Author overflo
# Part of frischluft.works
# Filename: led_driver.py
# Purpose: Blinks leds, Support both neopixel and RGB led
# License Details found @ /LICENSE file in this repository


import machine, neopixel
import time
import config


# This file handles the 10mm RGB led and the optional attached neopixels


## very old layout
#r_pin=27
#g_pin=25
#b_pin=32
# neopixel_pin = 4




if (config.HARDWARE_CONFIGURATION == 2):
    # wrover
    r_pin=12
    g_pin=13
    b_pin=14
else:
    # devboard
    r_pin=5
    g_pin=23
    b_pin=19

neopixel_pin = 18

neopixel_num = 3




np = neopixel.NeoPixel(machine.Pin(neopixel_pin), neopixel_num)




class LedDriver:
    def __init__(self):
        self.animation_running=0    

        #RGB led attached on pins 
        self.led_r = machine.PWM(machine.Pin(r_pin), freq=500)
        self.led_g = machine.PWM(machine.Pin(g_pin), freq=500)
        self.led_b = machine.PWM(machine.Pin(b_pin), freq=500)
        self.off()

        self.last_r=0
        self.last_g=0
        self.last_b=0

        self.alarmled = False
        
        self.wheelpos=0


    def set_led(self,r,g,b):

            # leds did not change? return.
            if (r == self.last_r) and (g == self.last_g) and (b == self.last_b):
                return


            #self.off()

            #print("rgb: %i %i %i" % (r,g,b))
            #print("r(t): %i" % self.translate(r))
            #print("g(t): %i" % self.translate(g))
            #print("b(t): %i" % self.translate(b))

            self.led_r.duty(self.translate(r))
            self.led_g.duty(self.translate(g))
            self.led_b.duty(self.translate(b))


            self.last_r=r
            self.last_g=g
            self.last_b=b


            for i in range(neopixel_num):
#                print(i)
                np[i] = (r,g,b)
            np.write()


    def off(self):
        # led OFF
        self.led_r.duty(self.translate(0))
        self.led_g.duty(self.translate(0))
        self.led_b.duty(self.translate(0))

        for i in range(neopixel_num):
            np[i] = (0,0,0)
        np.write()


    #takes a valur from 0-255 and returns a translated analog out value (1023-a fraction)
    def translate(self,value):
        if (config.HARDWARE_CONFIGURATION == 2):
            #invert for new transistor driven rgb leds on WROVER
            return int(value*1023/255)
        else:
           return 1023-int(value*1023/255)





    def alarm(self):

        # blink led red on alarm
        if not self.alarmled:
            self.set_led(255,0,0)
            self.alarmled=True
        else:
            self.set_led(0,0,0)
            self.alarmled=False

    def rainbowanimation(self):
        self.wheelpos+=1
        if self.wheelpos>255:
            self.wheelpos=0

        self.wheel(self.wheelpos)
        time.sleep(0.1)

    def wheel(self,wheelpos):
        wheelpos = 255 - wheelpos
        if wheelpos < 85:
            self.set_led(255 - wheelpos * 3, 0, wheelpos * 3)
            return

        if wheelpos < 170:
            wheelpos -= 85
            self.set_led(0, wheelpos * 3, 255 - wheelpos * 3)
            return

        wheelpos -= 170
        self.set_led(wheelpos * 3, 255 - wheelpos * 3, 0)
