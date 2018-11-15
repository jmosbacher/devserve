import requests
import ast
import json
from typing import Dict

class DeviceClient:
    _addr = ''
    def __init__(self, addr: str):
        self._addr = addr

    def __getattr__(self, item):
        try:
            resp = requests.get('{addr}/{item}'.format(addr=self._addr, item=item))
            if resp.ok:
                try:
                    val = ast.literal_eval(resp.json().get('value', None))
                except:
                    val = resp.json().get('value', None)
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


ClientDict = Dict[str, DeviceClient]

class SystemClient:

    def __init__(self, devices: ClientDict):
        self.devices = devices

    @classmethod
    def from_config_file(cls, host ,path: str):
        with open(path, "r") as f:
            cfgs = json.load(f)
        clients = {}
        for i, cfg in enumerate(cfgs):
            addr = f'http://{host}:{5000+i}/{cfg["name"]}'
            c = DeviceClient(addr)
            clients[cfg["name"]] = c
        return cls(clients)

    def set_state(self, states: dict):
        for name, state in states.items():
            dev = self.devices.get(name, {})
            for attr, val in state.items():
                setattr(dev, attr, val)

    def __getattr__(self, item):
        try:
            return self.devices.get(item)
        except:
            raise AttributeError('System has no device {}'.format(item))