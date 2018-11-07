
class Device:

    public = ['connected']

    def __init__(self, *args, **kwargs):
        pass

    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def __enter__(self):
        self.connect()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

class Echo(Device):
    public = ['echo','connected']
    connected = True
    _echo = ''
    
    @property
    def echo(self):
        return self._echo

    @echo.setter
    def echo(self, value):
        self._echo = value

    def connect(self):
        pass

    def disconnect(self):
        pass

    
