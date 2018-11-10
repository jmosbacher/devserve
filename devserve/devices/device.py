import random


class Device:
    _public = ('connected', 'attributes')
    public = []

    def __init__(self, *args, **kwargs):
        self.public.extend(self._public)

    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError
    
    @property
    def attributes(self):
        return self.public

    def __enter__(self):
        self.connect()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

class Debugger(Device):
    public = ['echo','random']
    connected = True
    _echo = 'echo'
    
    @property
    def echo(self):
        return self._echo

    @echo.setter
    def echo(self, value):
        self._echo = value

    @property
    def random(self):
        return random.random()

    def connect(self):
        pass

    def disconnect(self):
        pass


