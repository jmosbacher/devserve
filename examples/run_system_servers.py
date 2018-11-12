import json
import argparse
from devserve.servers import DeviceServer
from devserve.devices import device_directory
import time
from multiprocessing import Process
cfgs = []
import os
if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    cfg_path = os.path.join(dir_path, "device_config.json")
    with open(cfg_path, "r") as f:
        cfgs = json.load(f)

    servers = []
    host = 'localhost'

    for i, cfg in enumerate(cfgs):
        port = 5000+i
        try:
            device = device_directory[cfg["device"]](f'{cfg["com"]}')
            server = DeviceServer(cfg["name"], host, port, device)
            p = Process(target=server.run)
            print(f"starting device server for {cfg['name']}...")
            p.daemon = True
            p.start()
            servers.append(p)
            if p.is_alive():
                print(f"device server started. running on: {host}:{port}")

        except:
            pass

    try:
        while True:
            time.sleep(0.5)
    finally:
        for p in servers:
            p.terminate()
