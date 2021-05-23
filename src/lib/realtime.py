import ntptime
import time


class Realtime:

    active = False
    
    #TODO set via webinterface timezone
    houroffset = 1

    def __init__(self):
        self.active = False

    def start(self):
        try:
            ntptime.settime()
        except Exception as e:
            self.acive=False
            return

        self.active=True

    def set_houroffset(self,houroffset):
        self.houroffset=houroffset



    def get_time(self):
        if not self.active:
            return False

        t = time.localtime()

        return "%s-%s-%s %s:%s" % (t[0],t[1],t[2],t[3]+self.houroffset,t[5])