import serial
import struct
import time
from ..device import Device

class SolisProxy(Device):
    """
    Connects to a proxy script running in
    Andor solis, written with andor basic.
    """
    public = ['saved', 'running', 'save_path', 'grating', shutter,
              'wavelength', 'exposure', 'slit_width', 'port']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._port = kwargs.get('com', "COM1")
        self._path = kwargs.get('save_path', f"andor_file_{time.time()}")
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

    def query(self, q):
        self.conn.write(f'{q}\r'.encode())
        resp = self.conn.read(150)
        return resp.strip().decode()

    def command(self, cmd, *args):
        self.conn.write(f'{cmd}\r'.encode())
        self.conn.read(150)
        for arg in args:
            self.conn.write(f'{arg}\r'.encode())
        self.conn.read(150)

    @property
    def save_path(self):
        return self._path

    @save_path.setter
    def save_path(self, value):
        if isinstance(value, str):
            self._path = value
            self._saved = False

    @property
    def saved(self):
        return self._saved

    @saved.setter
    def saved(self, value):
        if value in [1, True, 'True', 'true']:
            self.command("Save", self._path)
            self._saved = True
        elif value in [0, False, 'False', 'false']:
            self._saved = False


    @property
    def shutter(self):
        return self.query("GetShutter")

    @shutter.setter
    def shutter(self, value):
        if value in [1, True, 'Open', 'open']:
            self.command("SetShutter", 1)
        elif value in [0, False, 'Closed', 'closed']:
            self.command("SetShutter", 0)

    @property
    def running(self):
        if self._running and (self.conn.read(150, timeout=0.2) == b'Done\r\n'):
            self._running = False
        return self._running

    @running.setter
    def running(self, running):
        # if running not in [True, False]:
        #     return
        if self._running:
            return
        elif running in [1, True, 'True']:
            self.command('Run')
            self._running = True
            self._saved = False

    @property
    def grating(self):
        return self.query("GetGrating")

    @grating.setter
    def grating(self, value):
        if value in [1, 2]:
            self.command("SetGrating", value)

    @property
    def wavelength(self):
        return self.query("GetWavelength")

    @wavelength.setter
    def wavelength(self, value):
        self.command("SetWavelength", value)

    @property
    def exposure(self):
        return self.query("GetExposureTime")

    @exposure.setter
    def exposure(self, value):
        self.command("SetExposureTime", value)

    @property
    def slit_width(self):
        return self.query("GetSlitWidth")

    @slit_width.setter
    def slit_width(self, value):
        self.command("SetSlitWidth", value)

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
            