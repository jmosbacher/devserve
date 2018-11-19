import requests
import ast
import json
from typing import Dict
import threading
import time


class DeviceClient:

    def __init__(self, name, addr: str):
        self._name = name
        self._addr = addr
        self._record_mode = 'None'
        self.__recording = set()
        self._record_delay = 10

    @property
    def _recording(self):
        return self.__recording

    @_recording.setter
    def _recording(self, value):
        if value in self.attributes:
            self.__recording.add(value)
        if len(self.__recording)==1:
            self._thread = threading.Thread(target=self.recorder)
            self._thread.setDaemon(True)
            self._thread.start()

    @property
    def _stop_recording(self):
        return set(self.attributes).difference(self.__recording)

    @_stop_recording.setter
    def _stop_recording(self, value):
        if value in self.__recording:
            self.__recording.remove(value)

    def recorder(self):
        from influxdb import InfluxDBClient
        influx = InfluxDBClient(host='localhost', port=8086)
        dbs = influx.get_list_database()
        if "recordings" not in [d['name'] for d in dbs]:
            influx.create_database("recordings")
        while True:
            if not len(self.__recording):
                break
            for attr in self.__recording:
                if self._record_mode is 'influx':
                    data = {
                        "measurement": attr,
                        "fields":{
                            "name": attr,
                            "device": self._name,
                            "value": getattr(self, attr)
                        }
                    }
                    influx.write_points([data], database="recordings")

                elif self._record_mode is 'mongo':
                    pass

                elif self._record_mode is 'file':
                    pass
            time.sleep(self._record_delay)


    def __getattr__(self, item):
        if item.startswith('_'):
            return super().__getattribute__(item)
        try:
            resp = requests.get('{addr}/{item}'.format(addr=self._addr, item=item))
            if resp.status_code is 200:
                val = None
                try:
                    val = resp.json().get('value', None)
                except:
                    pass
                try:
                    val = ast.literal_eval(resp.json().get('value', None))
                except:
                    pass
                return val
        except:
            raise AttributeError('Device address unavailable.')
        raise AttributeError('Attribute {} is not available'.format( item))

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
        else:
            try:
                resp = requests.put('{addr}/{key}'.format(addr=self._addr, key=key), data={"value": value})
                if resp.status_code is 201:
                    val = None
                    try:
                        val = resp.json().get('value', None)
                    except:
                        pass
                    try:
                        val = ast.literal_eval(resp.json().get('value', None))
                    except:
                        pass
                    return val
                else:
                    raise 'Bad response from server code: {}'.format(resp.status_code)
            except:
                raise AttributeError('Server unavailable.')


ClientDict = Dict[str, DeviceClient]

class SystemClient:

    def __init__(self, devices: ClientDict):
        self.devices = devices

    @classmethod
    def from_json_file(cls, host ,path: str):
        with open(path, "r") as f:
            cfgs = json.load(f)
        clients = {}
        for i, cfg in enumerate(cfgs):
            addr = f'http://{host}:{5000+i}/{cfg["name"]}'
            c = DeviceClient(name=cfg["name"],addr=addr)
            clients[cfg["name"]] = c
        return cls(clients)

    @classmethod
    def from_config_file(cls, path: str):
        import configparser
        config = configparser.ConfigParser()
        config.read(path)
        clients = {}
        for idx, name in enumerate(config.sections()):
            cfg = dict(config[name])
            for k,v in cfg.items():
                cfg[k] = v.format(idx=idx)
            addr = f'http://{cfg["host"]}:{cfg["port"]}/{name}'
            c = DeviceClient(name, addr)
            clients[cfg["name"]] = c
        return cls(clients)

    @classmethod
    def from_dict(cls, cfgs: str, host='localhost'):
        clients = {}
        for i, cfg in enumerate(cfgs):
            addr = f'http://{host}:{5000+i}/{cfg["name"]}'
            c = DeviceClient(cfg["name"], addr)
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