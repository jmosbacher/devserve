import json
import argparse
from devserve.clients import DeviceClient, SystemClient

host = 'localhost'
cfgs = []
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
cfg_path = os.path.join(dir_path, "device_config.json")
with open(cfg_path, "r") as f:
    cfgs = json.load(f)

def system_client():
    clients = {}
    for i, cfg in enumerate(cfgs):
        addr = f'{host}:{5000+i}'
        c = DeviceClient(addr)
        clients[cfg["name"]] = c
    return SystemClient(clients)