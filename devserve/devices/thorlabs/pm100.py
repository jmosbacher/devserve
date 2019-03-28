import serial
import struct
import time
import threading
from ..device import Device


class PM100(Device):
    public = ['power', 'count', 'port', 'wavelength', 'mode', 'autorange', 'recording', 'record_delay', 'save_path', 'saved' ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._port = kwargs.get('com', "USB0::0x1313::0x8072::P2005497::INSTR")
        self.pm = None
        self._recording = False
        self.record_delay = 0.1
        self._save_path = None
        self._saved = False
        self._cache = {"ts":[], "ms": []}

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
    def power(self):
        if self.pm is None:
            return
        return self.pm.read

    @property
    def count(self):
        if self.pm is None:
            return
        return self.pm.sense.average.count

    @count.setter
    def count(self, value):
        value = int(value)
        if self.pm is None:
            return
        if value >700:
            self.pm.sense.average.count = 700
            return
        elif value>0:
            self.pm.sense.average.count = value

    @property
    def wavelength(self):
        return self.pm.sense.correction.wavelength

    @wavelength.setter
    def wavelength(self, value):
        self.pm.sense.correction.wavelength = value

    @property
    def mode(self):
        return self.pm.getconfigure

    @property
    def autorange(self):
        return self.pm.sense.power.dc.range.auto is 1

    @autorange.setter
    def autorange(self, value):
        if value in [0, False, 'False', 'false', 'off']:
            self.pm.sense.power.dc.range.auto = 0
        elif value in [1, True, 'True', 'true','on']:
            self.pm.sense.power.dc.range.auto = 1

    def connect(self):
        try:
            import visa
            from ThorlabsPM100 import ThorlabsPM100
            rm = visa.ResourceManager()
            inst = rm.open_resource(self._port, timeout=1)
            self.pm = ThorlabsPM100(inst=inst)
        except:
            pass

    @property
    def connected(self):
        if self.pm is not None:
            return True
        return False

    @property
    def recording(self):
        return self._recording

    @recording.setter
    def recording(self, value):
        if self._recording == value:
            return
        elif self._recording and value==False:
            self._recording = False
        elif value==True:
            self._thread = threading.Thread(target=self.recorder)
            self._thread.setDaemon(True)
            self._thread.start()
            self._recording = True

    def recorder(self):
        ts = self._cache['ts']
        ms = self._cache['ms']
        while self._recording:
            t0 = time.time()
            ms.append(self.power)
            t1 = time.time()
            ts.append(t0/2 + t1/2)
            time.sleep(self.record_delay)
            
    @property
    def save_path(self):
        return self._save_path

    @save_path.setter
    def save_path(self, path):
        self._save_path = path
        self._saved = False

    @property
    def saved(self):
        return self._saved

    @saved.setter
    def saved(self, value):
        if self.save_path is None:
            return
        ts = self._cache['ts']
        ms = self._cache['ts']
        with open(self.save_path, 'w') as f:
            for t,m in zip(ts, ms):
                print(t, m, sep=',', file=f) 
        self._saved = True
        self._cache['ts'] = []
        self._cache['ts'] = []