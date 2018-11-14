from flask import Flask, url_for

from flask_restful import reqparse, abort, Api, Resource
import redis
import ast
rparser = reqparse.RequestParser()
rparser.add_argument('value')


class DeviceServer:

    def __init__(self, name, host, port, device, rs=None):
        self.name = name
        self.host = host
        self.port = port
        self.device = device
        self.rs = rs
        
    def run(self, debug=False):
        app = Flask(__name__)
        api = Api(app)

        class RestfulDevice(Resource):
            dev = self.device
            attrs = dev.public + dev._common
            def get(self, ep):
                if ep in self.attrs:
                    val = getattr(self.dev, ep)
                    return {"name":ep, "value" : val}
                else:
                    abort(f'No attribute named {ep}')
                
            def put(self, ep):
                if ep in self.attrs:
                    args = rparser.parse_args()
                    try:
                        val = ast.literal_eval(args['value'])
                    except:
                        val = args['value']
                    try:
                        setattr(self.dev, ep, val)
                        return {"name":ep, "value" : val}, 201
                    except:
                        abort(f'{ep} is not writable.')
                else:
                    abort(f'No attribute named {ep}')

        api.add_resource(RestfulDevice, f'/{self.name}/<ep>')

        try:
            self.device.connect()
            if self.rs is not None:
                self.rs.set(self.name, f'{self.host}:{self.port}')
            app.run(host=self.host, port=self.port, debug=debug)
            if self.rs is not None:
                self.rs.delete(self.name)

        except KeyboardInterrupt:
            print('User requested stop. Closing down gracefully...')
        except Exception as e:
            if debug:
                print(e)
            else:
                print('Exception raised. Closing down gracefully...')
        finally:
            if self.device.connected:
                self.device.disconnect()


