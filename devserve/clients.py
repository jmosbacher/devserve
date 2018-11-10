import requests
import ast

class DeviceClient:
    _addr = ''
    def __init__(self, addr):
        self._addr = addr

    def __getattr__(self, item):
        try:
            resp = requests.get('{addr}/{item}'.format(addr=self._addr, item=item))
            if resp.ok:
                try:
                    val = ast.literal_eval(resp.json()['value'])
                except:
                    val = resp.json()['value']
                return val
        except:
            raise AttributeError('Device address unavailable.')
        raise AttributeError('Attribute {} is not available'.format( item))

    def __setattr__(self, key, value):
        if key == '_addr':
            super().__setattr__(key, value)
        else:
            try:
                resp = requests.put('{addr}/{key}'.format(addr=self._addr, key=key), data={"value": value})
                if resp.ok:
                    return
                else:
                    raise 'Bad response from server code: {}'.format(resp.status_code)
            except:
                raise AttributeError('Server unavailable.')

class SystemClient:

    def __init__(self, devices):
        self.devices = devices

    def __getattr__(self, item):
        try:
            return self.devices.get(item)
        except:
            raise AttributeError('System has no device {}'.format(item))