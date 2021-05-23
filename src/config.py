
# Early 2021
# Author metachris && overflo
# Part of frischluft.works
# Filename: config.py
# Purpose: Provide Configuration values to the application 
# License Details found @ /LICENSE file in this repository

"""
Helper to easily and safely access configuration from the config json files

To add new config properties, do the following steps:

1. Add it to config-default.json (note: delete an existing config.json if exists on the device)
2. Add it here to CONFIG_TYPES
3. Add it here on the bottom of the file for easy access
"""

import json

CONFIG_FILENAME = 'config.json'
DEFAULT_CONFIG_FILENAME = 'config-default.json'

CONFIG_TYPES = {
    "wifiSsid": str,
    "wifiPassword": str,
    "adminPassword": str,
    "mqttServer": str,
    "mqttPort": int,
    "adminPassword": str,
    "deviceName": str,
    "mqttUsername": str,
    "mqttPassword": str,
    "thresholdWarningPpm": int,
    "thresholdAlertPpm": int,
    "isSoundOn": bool,
    "machineID": str,
    "softwareVersion": str,
}


def load_config():
    """
    Try to load the configuration from config.json.
    If not exists, create from default.
    """
    try:
        config_content_str = open(CONFIG_FILENAME).read()
    except Exception as err:
        print("Config file not found, resetting to default config.", err)
        config_content_str = reset_to_default_config()

    try:
        config_content = json.loads(config_content_str)
        return config_content
    except Exception as err:
        print('Error: could not load config.json')
        raise


def reset_to_default_config():
    print("resetting config.json to default")
    config_content_str = open(DEFAULT_CONFIG_FILENAME).read()
    with open(CONFIG_FILENAME, "w") as f:
        f.write(config_content_str)
    return config_content_str


def update_config_file(config_content):
    """
    Called with JSON payload from webserver. Make sure new config is valid and update config.json
    """
    global IS_SOUND_ON, THRESHOLD_ALERT_PPM, THRESHOLD_WARNING_PPM, DEVICE_NAME, ADMIN_PASSWORD, IS_CONFIGURED_BY_USER

    config_new = load_config()
    for key in config_content.keys():
        if not key in CONFIG_TYPES:
            continue

        if not isinstance(config_content[key], CONFIG_TYPES[key]):
            continue

        if config_new[key] != config_content[key]:
            print("update config with key", key, "->", config_content[key])
            config_new[key] = config_content[key]

            # Hot update current config, so we don't need to reboot
            if key == 'isSoundOn': IS_SOUND_ON = config_new[key]
            if key == 'thresholdWarningPpm': THRESHOLD_WARNING_PPM = config_new[key]
            if key == 'thresholdAlertPpm': THRESHOLD_ALERT_PPM = config_new[key]
            if key == 'adminPassword': ADMIN_PASSWORD = config_new[key]
            if key == 'deviceName': DEVICE_NAME = config_new[key]


    config_new['isConfiguredByUser'] = True
    IS_CONFIGURED_BY_USER = True

    # Save to file
    with open(CONFIG_FILENAME, "w") as f:
        f.write(json.dumps(config_new))


config_content = load_config()
print("Loaded config:", config_content)

WIFI_SSID = config_content["wifiSsid"]
WIFI_PASSWORD = config_content["wifiPassword"]
ADMIN_PASSWORD = config_content["adminPassword"]
IS_SOUND_ON = config_content["isSoundOn"]
MQTT_SERVER = config_content["mqttServer"]
MQTT_PORT = config_content["mqttPort"]
MQTT_USERNAME = config_content["mqttUsername"] or None
MQTT_PASSWORD = config_content["mqttPassword"] or None
THRESHOLD_WARNING_PPM = config_content["thresholdWarningPpm"]
THRESHOLD_ALERT_PPM = config_content["thresholdAlertPpm"]
DEVICE_NAME = config_content["deviceName"] #or "frischluft"  # warum sollte das per default auf irgendwas gesetzt sein?
ADMIN_PASSWORD = config_content["adminPassword"]
IS_CONFIGURED_BY_USER = config_content["isConfiguredByUser"]

HARDWARE_CONFIGURATION = 1 # 1 == esp32devboard   2 == ESP32-WROVER-B


import machine
id = machine.unique_id()
MACHINE_ID = '{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}'.format(id[0], id[1], id[2], id[3], id[4], id[5])

#Update hier
SOFTWARE_VERSION = config_content["softwareVersion"]


import uos
u = uos.uname()
#print(u[4])
#print(u[4].find("spiram"))
if(u[4].find("spiram") != -1):
    print("ESP32-WROVER-B DETECTED")
    HARDWARE_CONFIGURATION = 2
else:    
    print("ESP32-WROOM-DEVBOARD DETECTED")


