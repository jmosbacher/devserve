import serial
import struct
import time
from ..device import Device

class SolisProxy(Device):
    """
    Connects to a proxy script running in
    Andor solis, written with andor basic.
    """
    public = ['save', 'running', 'path', 'port']

    def __init__(self, port='COM7'):
        super().__init__()
        self._port = port
        self._path ='not_saved'
        self._running = False
        self.conn = None

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

    @property
    def save(self):
        return self._path

    @save.setter
    def save(self, path):
        self.conn.write(b'Save\r')
        self.conn.read(150)
        self.conn.write(path.encode()+b'\r')
        self.conn.read(150)
        self._path = path

    @property
    def running(self):
        if self._running and (self.conn.read(150) == b'Done\r\n'):
            self._running = False
        return self._running

    @running.setter
    def running(self, running):
        # if running not in [True, False]:
        #     return
        if self._running and (self.conn.read(150) != b'Done\r\n'):
            return
        elif running:
            self.conn.write(b'Run\r')

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