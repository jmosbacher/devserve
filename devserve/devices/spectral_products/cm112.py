import serial
import struct
import time
from ..device import Device
# from .. import device_directory


class CM112(Device):
    public = ['wavelength', 'grating', 'port', 'connected']
    @staticmethod
    def wl_to_bytes(wl):
        a = wl*10.
        high = int(a/256)
        low = int(a - high*256)
        return high, low

    @staticmethod
    def encode(*args):
        return b''.join([struct.pack('B',arg) for arg in args])

    def query(self, *args):
        msg = self.encode(*args)
        self.conn.write(msg)
        return self.conn.read(2048)
    
    def home(self):
        self.query(255,255,255)

    @property
    def wavelength(self):
        h,l = self.query(56,0)
        return (h*256+l)/10

    @wavelength.setter 
    def wavelength(self, wl):
        high, low = self.wl_to_bytes(wl)  #Set monochromator to wl
        while True:
            cwl = self.wavelength
            if abs(wl - cwl)<1:
                return 
            else:
                self.query(16, high, low)
                time.sleep(0.5)
    @property
    def grating(self):
        h,l = self.query(56,4)
        return l

    @grating.setter
    def grating(self,gr):
        if gr not in [1,2]:
            return 'Invalid grating number (must be 1 or 2)'
        while True:
            if self.grating==gr:
                break
            else:
                self.query(26,gr)
                time.sleep(4)
    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        if self.connected:
            self.disconnect()
        try:
            self.connect()
        except:
            pass

    def connect(self):
        self.conn  = serial.Serial(self._port, baudrate=9600, timeout=1)

    @property
    def connected(self):
        if self.conn:
            return self.conn.is_open()
        return False

    def disconnect(self):
        if self.connected:
            self.conn.close()

    def __init__(self, port):
        self._port = port
        try:
            self.connect()
        except:
            self.conn = None
        
# device_directory['CM112'] = CM112