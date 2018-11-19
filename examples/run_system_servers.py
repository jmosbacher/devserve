import argparse
import configparser
import time
from subprocess import PIPE, Popen
import os
import datetime
import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
myip = s.getsockname()[0]
s.close()
CLOSE_TIME = 4

def run(name, idx, cfg, debug=False):
    tags = cfg.pop('tags', '').split(' ')
    for k, v in cfg.items():
        cfg[k] = v.format(idx=idx, myip=myip)
    args = [sys.executable]
    args.append(cfg.pop('script', 'run_device_server.py'))

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
    parser.add_argument('-debug', '--debug', action='store_const', dest='debug',
                        const=True, default=False, help='Run server in debug mode.')
    parser.add_argument('-mongo', '--mongo', action='store_const', dest='mongo',
                        const=True, default=False, help='Update mongodb with address.')

    parser.add_argument('-influx', '--influx', action='store_const', dest='influx',
                        const=True, default=False, help='Update influxdb with address.')

    cmd_args = parser.parse_args()
    if cmd_args.mongo:
        import pymongo

        client = pymongo.MongoClient()
        db = client.device_servers
        addresses = db.addresses

    if cmd_args.influx:
        from influxdb import InfluxDBClient
        influx = InfluxDBClient(host='localhost', port=8086)
        dbs = influx.get_list_database()
        if cmd_args.debug:
            print("Influx dbs: ", dbs)
        if "device_servers" not in [d['name'] for d in dbs]:
            influx.create_database("device_servers")

    debug = cmd_args.debug
    config = configparser.ConfigParser()
    config.read(cmd_args.path)
    ps = {}
    restart = []

    for idx, name in enumerate(config.sections()):
        try:
            cfg = dict(config[name])
            p = run(name, idx, cfg, debug=debug)
            ps[name] = p

            doc = {'name': name,
                   'address': f"{cfg['host']}:{cfg['port']}/{name}",
                   "date": datetime.datetime.utcnow()}
            if cmd_args.mongo:
                addresses.update_one({'name': name}, {"$set": doc}, upsert=True)

            if cmd_args.influx:
                json = {
                    "measurement": name,
                    "fields": {"address": doc["address"]}, }
                influx.write_points([json], time_precision='s', database='device_servers')
        except:
            pass

    try:
        while True:
            for idx, (name, p) in enumerate(ps.items()):
                if p.poll() is not None:
                    restart.append((idx, name))
                    print(f"Looks like {name} has shutdown. Will try to restart.")

            for idx, name in restart:
                print(f"Trying to restart {name}.")
                try:
                    p = ps[name]
                    p.kill()
                    cfg = dict(config[name])
                    p = run(name, idx, cfg)
                    ps[name] = p
                except:
                    pass

            time.sleep(10)
            restart = []


    except KeyboardInterrupt as e:

        print("Trying to shut down gracefully...")
        for p in ps.values():
            if p.poll() is None:
                p.send_signal(2)
        print(f"Waiting {CLOSE_TIME} seconds for all processes to close...")
        for i in range(CLOSE_TIME):
            print(CLOSE_TIME-i)
            time.sleep(1)

    finally:
        for name, p in ps.items():
            p.send_signal(2)
            if p.poll() is None:
                print(f'{name} not responding. Killing process.')
                p.kill()
            if debug:
                print(f'sdtout for {name}: \n', p.stdout.read().decode())
        time.sleep(0.5)
