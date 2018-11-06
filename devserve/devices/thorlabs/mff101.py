# Stolen from some issue thread on github

from ..device import Device
# from .. import device_directory
import io,re,sys
import serial
from enum import Enum
import time

class Position(Enum):
    down = b"\x6A\x04\x00\x02\x21\x01"
    d = b"\x6A\x04\x00\x02\x21\x01"
    DOWN = b"\x6A\x04\x00\x02\x21\x01"
    D = b"\x6A\x04\x00\x02\x21\x01"
    up = b"\x6A\x04\x00\x01\x21\x01"
    u = b"\x6A\x04\x00\x01\x21\x01"
    UP = b"\x6A\x04\x00\x01\x21\x01"
    U = b"\x6A\x04\x00\x01\x21\x01"
    unknown = b''

class Status(Enum):
    down = b'*\x04\x06\x00\x81P\x01\x00\x02\x00\x00\x90'
    up = b'*\x04\x06\x00\x81P\x01\x00\x01\x00\x00\x90'
    query = b"\x29\x04\x00\x00\x21\x01"

try:
    import ftd2xx
    import ftd2xx.defines as constants
    class MFF101(Device):
        public = ['position', 'info','port', 'connected']
        # Raw byte commands for "MGMSG_MOT_MOVE_JOG".

        def __init__(self, port="37000021"):
            self._port = port.encode()
            self.motor = None
            self.connect()

        def connected(self):
            if self.motor is None:
                return False
            else:
                return True

        @property
        def port(self):
            return self._port

        @port.setter
        def port(self, value):
            self._port = value

        @property
        def position(self):
            if not self.connected:
                return 'unknown'
            self.motor.write(Status.query)
            mot_stat = self.motor.read(12)
            try:
                pos = Status(mot_stat).name
            except:
                pos = 'unknown'
            return pos

        @position.setter
        def position(self, pos):
            if pos in Position.__members__:
                cmd = Position[pos].value
                if cmd:
                    self.motor.write(cmd)

        @property
        def info(self):
            return ', '.join([f'{k}:{v}' for k,v in self.motor.getDeviceInfo().items()])

        def connect(self):
            try:
                motor = ftd2xx.openEx(self._port)
                motor.setBaudRate(115200)
                motor.setDataCharacteristics(constants.BITS_8, constants.STOP_BITS_1, constants.PARITY_NONE)
                time.sleep(.05)
                motor.purge()
                time.sleep(.05)
                motor.resetDevice()
                motor.setFlowControl(constants.FLOW_RTS_CTS, 0, 0)
                motor.setRts()
                self.motor = motor
            except:
                pass
        def disconnect(self):
            self.motor.close()
            self.motor = None

except:
    print('Failed to import ftd2xx. Cannot use MFF101.')