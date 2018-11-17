from ..device import Device

class Uno(Device):
    public = ['port']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.com = kwargs.get('com', 'COM1')

        self._dpins = [f'digital{x}' for x in range(14)]
        self._apins = [f'analog{x}' for x in range(6)]

    def __getattr__(self, item):
        if item in self._dpins:
            n = int(item.replace('digital', ''))
            return self.board.digital[n].read()

    def __setattr__(self, key, value):
        if key in self._dpins and value in [0,1]:
            n = int(key.replace('digital', ''))
            self.board.digital[n].write(value)
        else:
            super().__setattr__(key, value)

    def connect(self):
        try:
            from pyfirmata import Arduino, util
            self.board = Arduino(self._port)
            self.connected = True
        except:
            self.connected = False

