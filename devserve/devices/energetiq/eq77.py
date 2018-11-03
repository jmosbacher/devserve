from serial.rs485 import RS485
import time
from ..device import Device
# from .. import device_directory


class EQ77(Device):

    public = ['power', 'connected', 'port']

    def query(self, q):
        self.conn.write(q.encode())
        res = self.conn.readlines(2048)[-1].strip()
        return res.split(b' = ')[-1].decode()

    @property
    def power(self):
        return self.query('Q')

    @power.setter
    def power(self, pwr):
        pwr = int(pwr)
        if pwr>100 or pwr<15:
            return 'Requested power out of range 15-100'
        
        while True:
            p = self.power
            if p==pwr:
                return f'Power now at {pwr}%'
            elif p>pwr:
                self.query('D')
            elif p<pwr:
                self.query('U')
            time.sleep(0.2)

        
    def connect(self):
        try:
            self.conn = RS485(self._port, baudrate=9600, timeout=1)
        except:
            return f'Could not connect to port {self._port}.'

    @property
    def connected(self):
        if self.conn:
            return self.conn.is_open()
        return False

    def disconnect(self):
        if self.connected:
            self.conn.close()

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        self.connect()

    def __init__(self, port='COM1'):
        self._port = port
        
# device_directory['EQ77'] = EQ77

if __name__ == '__main__':
    with EQ77('COM8') as en:
        print(en.power)