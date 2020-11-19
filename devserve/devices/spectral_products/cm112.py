import serial
import struct
import time
from ..device import Device


class CM112(Device):
    public = [ 'grating', 'wavelength', 'port', "zero", "calibrate",
               "increment_m1", "decrement_m1", "increment_m2", "decrement_m2",
               "step_size", "step"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._port = kwargs.get('com', "COM1")
        self.conn = None
        self._zero_requested = False

    @staticmethod
    def wl_to_bytes(wl):
        a = wl*10.
        high = int(a/256)
        low = int(a - high*256)
        return high, low

    @staticmethod
    def encode(*args):
        return b''.join([struct.pack('B', arg) for arg in args])

    def query(self, *args):
        msg = self.encode(*args)
        self.conn.write(msg)
        return list(self.conn.read(2048))
    
    def home(self):
        self.query(255,255,255)

    @property   
    def zero(self):
        if self._zero_requested:
            self._zero_requested = False
            return self.query(52, 1)
        self._zero_requested = True
        return "Ready to zero, call again to confirm."
        
    @property   
    def calibrate(self):
        pass
    
    @calibrate.setter
    def calibrate(self, wl):
        high, low = self.wl_to_bytes(wl)
        self.query(18, high, low)
        time.sleep(0.1)
        return self.wavelength
        
    @property
    def wavelength(self):
        h, l, *_ = self.query(56, 0)
        return (h*256+l)/10

    @wavelength.setter 
    def wavelength(self, wl):
        high, low = self.wl_to_bytes(wl)  #Set monochromator to wl
        while True:
            cwl = self.wavelength
            if abs(wl - cwl)<1:
                break
            else:
                self.query(16, high, low)
                time.sleep(0.1)
                
    @property
    def grating(self):
        h,l, *_ = self.query(56, 4)
        return l

    @grating.setter
    def grating(self, gr):
        if gr not in [1,2]:
            return
        self.query(26, gr)
        while True:
            try:
                if self.grating==gr:
                    break
                time.sleep(2)
            except:
                pass

    @property
    def increment_m1(self):
        return self.query(7)

    @increment_m1.setter
    def increment_m1(self, val):
        if not isinstance(val, int):
            return
        for _ in range(val):
            _ = self.increment

    @property
    def increment_m2(self):
        return self.query(8)

    @increment_m2.setter
    def increment_m2(self, val):
        if not isinstance(val, int):
            return
        for _ in range(val):
            _ = self.increment_m2
        
    @property
    def decrement_m1(self):
        return self.query(1)

    @decrement_m1.setter
    def decrement_m1(self, val):
        if not isinstance(val, int):
            return
        for _ in range(val):
            _ = self.decrement

    @property
    def decrement_m2(self):
        return self.query(2)

    @decrement.setter
    def decrement_m2(self, val):
        if not isinstance(val, int):
            return
        for _ in range(val):
            _ = self.decrement_m2

    @property
    def step_size(self):
        return self.query(56, 6)

    @step_size.setter
    def step_size(self, value):
        return self.query(55, value)

    @property
    def step(self):
        return self.query(54)

    @step.setter
    def step(self, n):
        for _ in range(n):
            _ = self.step

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
        try:
            self.conn = serial.Serial(self._port, baudrate=9600, timeout=1)
        except:
            pass

    @property
    def connected(self):
        if self.conn:
            return self.conn.is_open
        return False

    def disconnect(self):
        if self.connected:
            self.conn.close()


