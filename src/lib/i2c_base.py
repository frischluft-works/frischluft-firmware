# this class provides basic i2c functionality
# attach to address, read bytes, write bytes


from machine import Pin, I2C


class i2cBase():

    addr = 0x0

    def __init__(self):
        #print("i2cBase init()")
        self.i2c =  I2C(-1, scl=Pin(22), sda=Pin(21))

    def write(self, buf):
        self.i2c.writeto(self.addr, buf)

    def read(self,nbytes):
        return self.i2c.readfrom(self.addr,nbytes)

    def readfrom(self,memaddr,nbytes):
        return self.i2c.readfrom_mem(self.addr, memaddr, nbytes)   

    def writeto(self,memaddr,data):
        self.i2c.writeto_mem(self.addr, memaddr, data)
    
    #scans the bus for device id
    def scan(self):
        return self.i2c.scan()

