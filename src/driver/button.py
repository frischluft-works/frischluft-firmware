# Early 2021
# Author overflo
# Part of frischluft.works
# Filename: button.py
# Purpose: Handles the button with uasyncio backend
# License Details found @ /LICENSE file in this repository


import machine 
from machine import Pin
import uasyncio as asyncio
from primitives.pushbutton import Pushbutton


#import os
#import config









#this should handle presses and set timeouts for
class Button:

    pin=None
    pb =None

    longpressed=False
    pressed=False

    def __init__(self, pin):
        #print("button.__init__("+str(pin)+")")


        self.pin =  Pin(pin, Pin.IN)
 
        #apply to prototype class .. ok?! weird but.. ok.
        Pushbutton.long_press_ms=5000  # 5 second button down = calibration

        self.pb = Pushbutton(self.pin)
        self.pb.press_func(self.press, ())  # Note how function and args are passed
        self.pb.long_func(self.longpress, ())  # Note how function and args are passed

    #todo ask chris how to implement global variables or a better mechanism to trigger calibration
    def press(self):
        self.pressed=True
        print("button press") 


    def longpress(self):
        #not working calibrate_sensor .. some namespace problem :(
        self.longpressed=True
        print("button longpress")




#if __name__ == "__main__":
#    Button(36)
#    loop = asyncio.get_event_loop()
#    loop.run_forever()
