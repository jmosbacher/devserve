import serial
import struct
import time
from ..device import Device

class SolisProxy(Device):
    """
    Connects to a proxy script running in
    Andor solis, written with andor basic.
    """
    public = ['save', 'running', 'save_path', 'saved', 'port']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._port = kwargs.get('com', "COM1")
        self._path = 'not_saved'
        self._saved = False
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
    def save_path(self):
        return self._path

    @save_path.setter
    def save_path(self, path):
        self._path = path
        self._saved = False

    @property
    def saved(self):
        return self._saved

    @saved.setter
    def saved(self, value):
        if value in [1, True, 'True']:
            self.conn.write(b'Save\r')
            self.conn.read(150)
            self.conn.write(self._path.encode()+b'\r')
            self.conn.read(150)
            self._saved = True

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
        elif running in [1, True, 'True']:
            self.conn.write(b'Run\r')
            self._running = True


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