# Early 2021
# Author overflo
# Part of frischluft.works
# Filename: mqtt.py
# Purpose: Send MQTT messages to the broker
# License Details found @ /LICENSE file in this repository
# 


import config
from lib.umqttsimple import MQTTClient



class AmpelMqtt:
    mqtt_client = None
    connected = False

    def __init__(self):


        self.mqtt_client = MQTTClient(config.MACHINE_ID, config.MQTT_SERVER, config.MQTT_PORT, config.MQTT_USERNAME, config.MQTT_PASSWORD)
        #print (self.mqtt_client)

    def connect(self):
        if not config.MQTT_SERVER:
            print("no MQTT server configured")

            self.connected = False
            return False


        print("mqtt: connecting to %s:%s" % (config.MQTT_SERVER, config.MQTT_PORT))

        if self.connected:
            self.mqtt_client.disconnect()

        try:
            self.mqtt_client.connect()
            self.connected = True
            self.mqtt_client.publish(b"FRISCHLUFT/" + str(config.MACHINE_ID) + "/status", "CONNECTED")
            return True
        except Exception as e:
            self.connected = False
            print("MQTT connection FAILED error", e)
            return False

    def send_mqtt(self, measurement):



        print ("send_mqtt() called")
        if not self.connected: 
            print("MQTT not connected .. trying reconnect")
            if not self.connect(): return

        if not self.mqtt_client.sock: 
            print("MQTT no socket! .. trying reconnect")
            if not self.connect(): 
                self.connected = False
                return

        try:
            print("sending measurement: " + str(measurement))
            self.mqtt_client.publish(b"FRISCHLUFT/" + str(config.MACHINE_ID) + "/values/raw/co2", str(measurement))
        except Exception as e:
            print("Sending failed")
            self.connected = False
            self.mqtt_client.disconnect()
            pass

    def destroy(self):
        self.mqtt_client.disconnect()
