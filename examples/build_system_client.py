import json
from devserve.clients import DeviceClient, SystemClient
import argparse
import configparser
import time
from subprocess import PIPE, Popen
import os
import datetime
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
myip = s.getsockname()[0]
s.close()
CLOSE_TIME = 4

def run(name, idx, cfg, debug=False):
    tags = cfg.pop('tags', '').split(' ')
    for k, v in cfg.items():
        cfg[k] = v.format(idx=idx, myip=myip)

    args = cfg.pop('command', 'python run_device_server.py').split(' ')
    args.extend(['--name', name])
    for k, v in cfg.items():
        args.extend([f'--{k}', f'{v}'])
    args.extend([f'--{x}' for x in tags])
    print(f"starting device server for {name}...")
    if debug:
        print(f"command: ", args)
    p = Popen(args, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    print(f'device server for {name} started. running on: {cfg["host"]}:{cfg["port"]}')

    return p


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    default_path = os.path.join(dir_path, "system_config.conf")

    parser = argparse.ArgumentParser(description='Start device webservers from config file.')
    parser.add_argument('-FILE', '--FILE', dest='path', default=default_path,
                        help=f'Path to a valid config file.')
    cmd_args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(cmd_args.path)