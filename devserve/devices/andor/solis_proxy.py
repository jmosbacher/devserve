import serial
import struct
import time
from ..device import Device
import ast
class SolisProxy(Device):
    """
    Connects to a proxy script running in
    Andor solis, written with Andor BASIC.
    """

    public = ['saved', 'running', 'save_path', 'grating', 'shutter',
              'wavelength', 'exposure', 'slit_width', 'port', 'baud']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._port = kwargs.get('com', "COM1")
        self._baud = kwargs.get('baud', 38400)
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

    @property
    def baud(self):
        return self._baud

    @baud.setter
    def baud(self, value):
        if value in [4800, 9600, 14400, 19200, 38400, 57600, 115200]:
            self._baud = value
        self.connect()

    def query(self, q):
        self.conn.write(f'{q}\r'.encode())
        resp = self.conn.read(150)
        resp = resp.strip().decode()
        return resp

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
    def clear_screen(self):
        self.command("ClearScreen")
        return 'clear'

    @clear_screen.setter
    def clear_screen(self, value):
        if value in [True, 'clear']:
            self.command("ClearScreen")

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
            self.command("SetShutter", "open")
        elif value in [0, False, 'Closed', 'closed']:
            self.command("SetShutter", 'close')
        else:
            self.command("SetShutter", 'auto')

    @property
    def running(self):
        if self._running and (self.conn.read(150) == b'Done\r\n'):
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
        while True:
            if self.grating == f"{value}":
                break
            else:
                time.sleep(4)

    @property
    def wavelength(self):
        return self.query("GetWavelength")

    @wavelength.setter
    def wavelength(self, value):
        if (2000 >= value >= 200):
            self.command("SetWavelength", value)

    @property
    def exposure(self):
        return self.query("GetExposureTime")

    @exposure.setter
    def exposure(self, value):
        self.command("SetExposureTime", value)

    @property
    def slit_width(self):
        return self.query("GetSlit")

    @slit_width.setter
    def slit_width(self, value):
        if (2500 >= value >=10):
            self.command("SetSlit", value)

    def connect(self):
        self.disconnect()
        try:
            self.conn = serial.Serial(self._port, baudrate=self._baud, timeout=0.2)
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
            