from ..device import Device


class PRMTZ8(Device):
    public = ['position', 'port', 'zero', 'step', 'direction']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._port = kwargs.get('com', 27503140)
        self._motor = None
        self._zero = kwargs.get('zero', None)
        self._direction = -1
        self._step = kwargs.get('step', -30)
        self._pos_mapper = {}
        self._make_mapper()

    def _make_mapper(self):
        base = self._step*self._direction
        self._pos_mapper = {x: (self._zero + base * x if x < 7 else
                                self._zero - base * (12 - x))
                            for x in range(12)}

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = value
        self._make_mapper()

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, value):
        self._step = value
        self._make_mapper()

    @property
    def zero(self):
        return self._zero

    @zero.setter
    def zero(self, value):
        self._zero = value
        self._make_mapper()

    @property
    def position(self):
        if self._motor is None:
            return
        deg = self._motor.position
        pos = (deg-self._zero)/self._step
        return int(pos)

    @position.setter
    def position(self, pos):
        if self._motor is None or pos not in self._pos_mapper:
            return
        deg = self._pos_mapper[pos]
        self._motor.move_to(deg, blocking=True)


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
            if self._zero is None:
                self._zero = self._motor.position
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