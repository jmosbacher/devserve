from ..device import Device
import thorlabs_apt as apt


class K10CR1(Device):
    public = ['position', 'port', 'zero', 'step']

    def __init__(self, port=27503140, zero=0, step=30):
        super().__init__()
        self._port = port
        self._motor = None
        self._zero = zero
        self._step = step

    @property
    def position(self):
        deg = self._motor.position
        pos = (deg-self._zero)/self._step
        return int(pos)

    @position.setter
    def position(self, pos):
        deg = self._zero + pos/self._step
        self._motor.move_to(deg, True)

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, value):
        self._step = value

    @property
    def zero(self):
        return self._zero

    @zero.setter
    def zero(self, value):
        self._zero = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        self.connect()

    def connect(self):
        if self.connected:
            return
        try:
            self.motor = apt.Motor(self._port)
        except:
            pass

    def disconnect(self):
        self.motor = None
        self.apt._cleanup()

    @property
    def connected(self):
        if self._motor is None:
            return False
        return True