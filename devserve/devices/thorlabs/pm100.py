import serial
import struct
import time
from ..device import Device


class PM100(Device):
    def __init__(self, port='USB0::0x1313::0x8072::P2005497::INSTR'):

        super().__init__()
        self.pm = None
        self._port = port

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
            import visa
            from ThorlabsPM100 import ThorlabsPM100
            rm = visa.ResourceManager()
            inst = rm.open_resource(self._port, term_chars='\n', timeout=1)
            self.pm = ThorlabsPM100(inst=inst)
        except:
            pass

    @property
    def connected(self):
        if self.pm is not None:
            return True
        return False