import requests

class DeviceClient:

    def __init__(self, addr):
        self._addr = addr

    def __getattr__(self, item):
        resp = requests.get('{addr}/{item}'.format(addr=self._addr, item=item).replace('//','/'))
        if resp.ok:
            return resp.json()['value']
        else:
            raise AttributeError('Attribute {} is not available'.format( item))


class SystemClient:

    def __init__(self, devices):
        self.devices = devices

    def __getattr__(self, item):
        try:
            return self.devices.get(item)
        except:
            raise AttributeError('System has no device {}'.format(item))