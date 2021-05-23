# Early 2021
# Author  overflo some parts by metachris
# Part of frischluft.works
# Filename: start.py
# Purpose: Included from main.py to be compiled in .mpy, Here is the main porgram code 
# Start at line ~ 540 
# License Details found @ /LICENSE file in this repository



"""
Main entry point

- Sets everything up (sensors, display, network, mqtt, etc.)
- `measureTask` is run every second which collects and publishes data
- webserver is running in the background (port 80)
"""
import os
import gc
import sys
import network
import socket
import time
import uasyncio as asyncio
#import ntptime

#from time import sleep

#from driver import aht10




from driver import led_driver
from driver import buzzer_piezo
from driver import display
from driver import mhz19
from driver import button
from driver import mqtt

#NO MORE MEMORY :(
#from driver.bmp180 import BMP180


# import? -> OUT OF MEMORY
#from driver.aht10 import AHT10




# dns is broken when too many requests hit :(
from lib import dns
#from lib import realtime
from lib import databuffer

import config

import webserver

import esp32
import math

import machine













IS_UASYNCIO_V3 = hasattr(asyncio, "__version__") and asyncio.__version__ >= (3,)


DNS_ENABLED = False  # Disabled because "DNS server error: memory allocation failed, allocating 4097 bytes"


# Helper for REPL usage
def rmconfig():
    print("Deleted config")
    os.remove(config.CONFIG_FILENAME)




def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return int(math.floor(n * multiplier) / multiplier)




my_ip="frischluft AP"

# set true if button pressed on power on
erase_config = False

calibrate_sensor = False

# Helper to connect to wifi
async def wifi_connect(timeout_sec=10):
    global my_ip
    sta_if = network.WLAN(network.STA_IF)
    print("wifi: connecting to %s / %s" % (config.WIFI_SSID, config.WIFI_PASSWORD))
    time_started = time.time()

    if not sta_if.isconnected():
        # print('connecting to network...')
        sta_if.active(True)
        if config.DEVICE_NAME:
            sta_if.config(dhcp_hostname=config.DEVICE_NAME)

        sta_if.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

        while not sta_if.isconnected() and sta_if.status() == network.STAT_CONNECTING:
            await asyncio.sleep_ms(100)
            if time.time() > time_started + timeout_sec:
                sta_if.active(False)
                return False

    print('network config:', sta_if.ifconfig())
    my_ip = sta_if.ifconfig()[0]
    return True


ACCESSPOINT_SERVER_IP = '10.0.0.1'
def wifi_start_access_point():
    """ setup the access point """
    SERVER_SSID = 'frischluft'  # max 32 characters
    SERVER_SUBNET = '255.255.255.0'

    print("wifi: starting access point...")
    wifi = network.WLAN(network.AP_IF)
    wifi.active(True)
    wifi.ifconfig((ACCESSPOINT_SERVER_IP, SERVER_SUBNET, ACCESSPOINT_SERVER_IP, ACCESSPOINT_SERVER_IP))
    wifi.config(essid=SERVER_SSID, authmode=network.AUTH_OPEN)
    print('network config: ssid=%s' % SERVER_SSID, wifi.ifconfig())


def _handle_exception(loop, context):
    """ uasyncio v3 only: global exception handler """
    print('Global exception handler')
    sys.print_exception(context["exception"])
    print("start.py -> _handle_exception called from uasyncio v3")
    #sys.exit()



FRISCHLUFT_STATE_OK = 'FRISCHLUFT_STATE_OK'
FRISCHLUFT_STATE_WARNING = 'FRISCHLUFT_STATE_WARNING'
FRISCHLUFT_STATE_ALERT = 'FRISCHLUFT_STATE_ALERT'

class Frischluft:

    # objects later initalized
    leds = None
    display = None
    buzzer = None
    sensor = None
    webserver = None
    button = None
    bmp180 = None
    aht=None

    # internal variables
    access_point = False   # set if we open our own AP
    play_alarmsound = True # set on alarm() to notify only once

    last_mqtt_update = time.time()  # to send MQTT updates every minute
    active = True  # set true once sensor is warmed up.. used to flush display once

    #current_state = FRISCHLUFT_STATE_OK
    frischluft_state = FRISCHLUFT_STATE_OK

    had_alert = False

    async def start(self):


        # Get the event loop
        loop = asyncio.get_event_loop()

        # Add global exception handler
        if IS_UASYNCIO_V3:
            loop.set_exception_handler(_handle_exception)




        # Setup Button (pin 36)
        if (config.HARDWARE_CONFIGURATION == 2):
             # ESP32-WROVER-B
            self.button = button.Button(35)
        else:
            #devboard            
            self.button = button.Button(36)

        # Setup display
        self.display = display.Display()

 


        #"we get here if the button is pressed during power up"
        if erase_config:
            self.display.show_config_erase()
            rmconfig()
            self.display.show_restart()
            machine.reset()

        self.display.show_hello()



        # Setup LEDs
        self.leds = led_driver.LedDriver()
        self.leds.set_led(0, 0, 255)
        time.sleep(0.3)
        self.leds.set_led(255, 0, 0)
        time.sleep(0.3)
        self.leds.set_led(0, 255, 0)



        # initialize sensor on UART #2 (pin 16+17 on EP32)
        self.display.paint_text('Sensor', 0, 20)
        self.sensor = mhz19.mhz19()
        self.display.paint_text('OK', 60, 20)


        '''
        #pressure sensor
        self.bmp180 = BMP180()
        self.bmp180.oversample_sett = 3
        self.bmp180.baseline = 101325

        temp = self.bmp180.temperature
        p = self.bmp180.pressure
        altitude = self.bmp180.altitude

        print(temp, p, altitude)
        '''

        self.is_access_point = False

        if config.WIFI_SSID:
            # Start the wifi AP
            self.display.paint_text('WLAN', 0, 30)

            is_connected = await wifi_connect()
            if is_connected:
                print("wifi: conntected to %s" % config.WIFI_SSID)
                self.display.paint_text('OK', 60, 30)
                #print("sleeping 5 seconds ..waiting for wifi to sync")
                #time.sleep(5)
            else:
                self.display.paint_text('ERROR', 60, 30)
                self.is_access_point = True
        else:
            self.is_access_point = True

        if self.is_access_point:
            self.display.paint_text('Starte AP', 0, 40)
            self.display.paint_text('frischluft', 0, 50)
            #self.display.paint_text('10.0.0.1', 0, 56)


            wifi_start_access_point()

        # Create the webserver and add task to event loop
        self.webserver = webserver.app.run(host='0.0.0.0', port=80, loop_forever=False)



        # RE-ENABLE ONCE A SOLUTION TO MEMORY EXHAUSTION IS FOUND
        # Start the DNS server task
        if DNS_ENABLED:
          loop.create_task(self.run_dns_server())


        # Setup buzzer (pin 26)
        self.buzzer = buzzer_piezo.BuzzerPiezo(26)



        # Connect MQTT
        if not self.is_access_point:
            self.display.paint_text('MQTT', 0, 40)
            self.mqtt = mqtt.AmpelMqtt()

        # Only start MQTT if not in AP mode
        #if is_access_point:
        #    self.display.paint_text('SKIP', 60, 40)

        # print("MQTT success", is_mqtt_connected, self.mqtt.is_connected)
        #if not self.is_access_point:

            print("Verbinde MQTT...")
            self.mqtt.connect()
            self.display.paint_text('OK' if self.mqtt.connected else "ERROR", 60, 40)

        # Buzzer: play setup-success sound
        self.buzzer.turn_on_sound()

        #self.buzzer.alarm()

        # Finish setup
        self.display.flush()
        #sleep(1)


        aht=AHT10()
        if aht.active:
            self.aht=AHT10()



        # Measure
        loop.create_task(self.measureTask())

        # Start looping forever
        print('Looping forever...')
        loop.run_forever()

    async def measureTask(self):

        while True:
            try:

                # this block is for calibration after button long press
                if self.button.longpressed:
                    print("button pressed calibrating sensor")
                    self.display.show_calibration()
                    calib_started = time.time()
                    #regenbogen fuer 20 minuten..
                    while time.time() < calib_started + ( 20*60 ):
                        self.leds.rainbowanimation()

                    self.sensor.calibrate()
                    self.buzzer.oneup()
                    self.display.flush()
                    self.button.longpressed=False



                # this block is for calibration after button long press
                if self.button.pressed:
                    print("button pressed! - Display info")
                    self.display.show_info()
                    time.sleep(10)
                    self.display.flush()
                    self.button.pressed=False







                #gc.collect()
                self.sensor.get_data()

                if self.sensor.warm == False:
                    print("410 - Sensor Warmup..")
                    await asyncio.sleep_ms(5000) # come back in 5 seconds
                    self.display.flush()
                    self.display.paint_text("Sensor.init()", 0, 0)
                    #self.oled.text(str(ppm), 50, 20,3)
                    self.display.paint_text("Bitte warten..", 0, 25)
                    self.display.paint_text(my_ip,0,55)

                    self.display.show()
                    self.active=False
                    continue
                else:
                    if not self.active :
                        self.display.flush()
                        self.active=True

                # Collectcurrent sensor values

                ppm = self.sensor.ppm
                #temp = self.sensor.temp
                #co2status = self.sensor.co2status
                #hall = esp32.hall_sensor()
                # esp32_temp_f = esp32.raw_temperature()
                # esp32_temp_c = (esp32_temp_f - 32) * 5 / 9

                print("ppm: %s" % (ppm))

                # if we have a 0 value there was a communication problem with the sensor, do nothing, walk on.
                if ppm == 0:
                    await asyncio.sleep_ms(1000)
                    continue



                if(self.aht):
                    #print("hier")
                    self.aht.update()
                    databuffer.add_datapoint('temp', self.aht.temperature)
                    databuffer.add_datapoint('humidity', self.aht.humidity)



                databuffer.add_datapoint('ppm', ppm)
                #databuffer.add_datapoint('temp', temp)
                #databuffer.add_datapoint('hall', hall)
                # databuffer.add_datapoint('esp32_temp_c', esp32_temp_c)



                #self.display.show_messwert(round_down(ppm,-2))

                self.display.paint_messwert(ppm)

                if self.is_access_point:
                    self.display.paint_text("http://" + ACCESSPOINT_SERVER_IP, 1, 55)
                    self.display.paint_text('AP "frischluft"',0,41)
                else:
                    self.display.paint_text("http://", 1, 42)
                    self.display.paint_text(my_ip, 1, 55)




                    #send MQTT every minute
                    if time.time() > (self.last_mqtt_update + 60):
                        self.last_mqtt_update=time.time()
                        self.mqtt.send_mqtt(ppm)


                self.display.show()



                # this triggers the actual logic.. "what to do if sensor hits threshold"
                if ppm >= config.THRESHOLD_ALERT_PPM:
                    self.alert()
                elif ppm >= config.THRESHOLD_WARNING_PPM:
                    self.warning()
                else:
                    self.this_is_fine()

                # Sleep 1 seconds
                await asyncio.sleep_ms(1000)


            except Exception as e:
                print("Something weird happened in start.py around line 455")
                print(e)



    def alert(self):
        #    print("alert() called ")
        self.leds.alarm()

        # play only once, even on long alert state
        if self.frischluft_state != FRISCHLUFT_STATE_ALERT:
            self.buzzer.alarm()

        self.frischluft_state = FRISCHLUFT_STATE_ALERT
        self.had_alert = True


    def warning(self):
        # print("warning() called ")
        self.leds.set_led(255, 255, 0)

        # play once when going from green to yellow
        if self.frischluft_state == FRISCHLUFT_STATE_OK:
            self.buzzer.alarm()

        # Update the state
        self.frischluft_state = FRISCHLUFT_STATE_WARNING


    def this_is_fine(self):
        #print("all good")
        self.leds.set_led(0, 255, 0)

        # true if we come back from red alert
        # lets play a oneup sound for turning green again
        if self.had_alert:
            self.buzzer.oneup()
            self.had_alert = False

        self.frischluft_state = FRISCHLUFT_STATE_OK


    # needed fro captive portal ,but breaks with Out of Memory from time to time.. not initalized any longer
    # it would be cool to enable this again but it needs some fiddely frobbely magical surgery that i can not do at this time
    async def run_dns_server(self):
        """ function to handle incoming dns requests """
        udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udps.setblocking(False)
        udps.bind(('0.0.0.0', 53))

        while True:
            try:
                #print(str(gc.mem_free()) + " before ")
                if gc.mem_free() < 5000 :
                    print("OOM in DNS :( returning")
                    return  # to prevent out of memory bug
                #print(str(gc.mem_free()) + " after")
                if IS_UASYNCIO_V3:
                    yield asyncio.core._io_queue.queue_read(udps)
                else:
                    yield asyncio.IORead(udps)

                print(1)
                data, addr = udps.recvfrom(4096)
                # print("Incoming DNS request...")
                print(2)

                DNS = dns.DNSQuery(data)
                print(3)
                udps.sendto(DNS.response(ACCESSPOINT_SERVER_IP), addr)
                print(4)

                print("DNS: {:s} -> {:s}".format(DNS.domain, ACCESSPOINT_SERVER_IP))

            except Exception as e:
                print("DNS server error:", e, gc.mem_free())
                await asyncio.sleep_ms(3000)

        udps.close()






# Main code entrypoint
try:

    # read button.
    # is it pressed during boot? set erase flag.
    if (config.HARDWARE_CONFIGURATION == 2):
        # WROVER
        b = machine.Pin(35, machine.Pin.IN)
    else:
        #DEVBOARD
        b = machine.Pin(36, machine.Pin.IN)
            
    time.sleep(0.2)
    if b.value():
        print("Button down")
        erase_config=True

    # Instantiate app and run
    myapp = Frischluft()

    # This was introduced for backwards compatibility ith older micropython revisions.
    # TODO: remove?!
    if IS_UASYNCIO_V3:
        asyncio.run(myapp.start())
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(myapp.start())

except KeyboardInterrupt:
    print('Bye')

finally:
    if IS_UASYNCIO_V3:
        asyncio.new_event_loop()  # Clear retained state

