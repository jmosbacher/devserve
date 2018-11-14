from ..device import Device


class PRMTZ8(Device):
    public = ['position', 'port', 'zero', 'step']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._port = kwargs.get('com', 27503140)
        self._motor = None
        self._zero = kwargs.get('zero', 0)
        self._step = kwargs.get('step', 30)

    @property
    def position(self):
        if self._motor is None:
            return
        deg = self._motor.position
        pos = (deg-self._zero)/self._step
        return int(pos)

    @position.setter
    def position(self, pos):
        if self._motor is None:
            return
        deg = self._zero + pos*self._step
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
            import thorlabs_apt as apt
            self._motor = apt.Motor(self._port)
        except:
            pass

    def disconnect(self):
        try:
            import thorlabs_apt as apt
            self._motor = None
            apt.core._cleanup()
        except:
            pass
            
    @property
    def connected(self):
        if self._motor is None:
            return False
        return True