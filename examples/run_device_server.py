import argparse
from devserve.device_server import DeviceServer

from devserve.devices.device import Device
from devserve.devices import device_directory

# device_directory = {cls.__name__: cls for cls in Device.__subclasses__()}

if __name__ == '__main__':
    device_names = list(device_directory.keys())
    device_names_str = ",".join(device_names)
    parser = argparse.ArgumentParser(description='Start an device webserver.')
    parser.add_argument('-DEVICE', '--DEVICE', dest='device', default='Echo',
                choices=device_names, help=f'Device to control. Default is: Echo.')
    parser.add_argument('-NAME', '--NAME', dest='name', default='dev',
                help='Device name, must be unique.')
    parser.add_argument('-COM', '--COM', dest='com', default=1,
                help='Serial port.')
    parser.add_argument('-HOST', '--HOST',dest='host',default='localhost',
                help='IP to serve on.')
    parser.add_argument('-PORT', '--PORT',dest='port', type=int, default=5000,
            help='Port to open.')
    parser.add_argument('-DEBUG', '--DEBUG', action='store_const', dest='debug',
                const=True, default=False, help='Run server in debug mode.')
    kwargs = vars(parser.parse_args())
    device = kwargs['device']
    name = kwargs['name']
    host = kwargs['host']
    port = kwargs['port']
    com = kwargs['com']
    debug= kwargs['debug']
    device = device_directory[device](f'{com}')
    server = DeviceServer(name, host, port, device)
    server.run(debug=debug)