Contains a copy of the micropython 1.15 release
This is necessary when you build the code from source yourself, but NOT NEEDED if you flash a premade release .bin file


#how to install micropython 1.15

esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 80m --flash_size detect 0x1000 esp32-20210418-v1.15.bin  

