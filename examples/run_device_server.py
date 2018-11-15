import argparse
from devserve.servers import DeviceServer

from devserve.devices.device import Device
from devserve.devices import device_directory


# device_directory = {cls.__name__: cls for cls in Device.__subclasses__()}

if __name__ == '__main__':
    device_names = list(device_directory.keys())
    device_names_str = ",".join(device_names)
    parser = argparse.ArgumentParser(description='Start an device webserver.')
    parser.add_argument('-DEVICE', '--DEVICE', dest='device', default='Debugger',
                choices=device_names, help=f'Device to control. Default is: Debugger.')
    parser.add_argument('-NAME', '--NAME', dest='name', default='debug',
                help='Device name, must be unique.')
    parser.add_argument('-COM', '--COM', dest='com', default='COM1',
                help='Serial port.')
    parser.add_argument('-HOST', '--HOST',dest='host',default='localhost',
                help='IP to serve on.')
    parser.add_argument('-PORT', '--PORT',dest='port', type=int, default=5000,
            help='Port to open.')
    parser.add_argument('-DEBUG', '--DEBUG', action='store_const', dest='debug',
                const=True, default=False, help='Run server in debug mode.')
    parser.add_argument('-REDIS', '--REDIS', action='store_const', dest='set_redis',
                        const=True, default=False, help='Set address in redis.')
    parsed, unknown = parser.parse_known_args()  # this is an 'internal' method
    # which returns 'parsed', the same as what parse_args() would return
    # and 'unknown', the remainder of that
    # the difference to parse_args() is that it does not exit when it finds redundant arguments

    for arg in unknown:
        if arg.startswith(("-", "--")):
            # you can pass any arguments to add_argument
            parser.add_argument(arg,)

    a = parser.parse_args()

    if a.set_redis:
        import redis
        rs = redis.Redis("localhost")
    else:
        rs = None

    device = device_directory[a.device](**vars(a))
    server = DeviceServer(a.name, a.host, a.port, device, rs)
    server.run(debug=a.debug)