from flask import Flask, url_for

from flask_restful import reqparse, abort, Api, Resource
import redis
rparser = reqparse.RequestParser()
rparser.add_argument('value')


class DeviceServer:

    def __init__(self, name, host, port, device):
        self.name = name
        self.host = host
        self.port = port
        self.device = device
        
    def run(self, debug=False):
        app = Flask(__name__)
        api = Api(app)

        class RestfulDevice(Resource):
            dev = self.device
            
            def get(self, ep):
                if ep in self.dev.public:
                    resp = getattr(self.dev, ep)
                    return {ep: resp}
                else:
                    abort(f'No attribute named {ep}')
                
            def put(self, ep):
                if ep in self.dev.public:
                    args = rparser.parse_args()
                    val = args['value']
                    try:
                        setattr(self.dev, ep, val)
                        return {ep: val}, 201
                    except:
                        abort(f'{ep} is not writable.')
                else:
                    abort(f'No attribute named {ep}')

        api.add_resource(RestfulDevice, f'/{self.name}/<ep>')

        @app.route(f'/{self.name}/attributes')
        def attributes():
            return "\n".join(RestfulDevice.dev.public)
        rs = redis.Redis("localhost")
        try:
            app.run(host=self.host, port=self.port, debug=debug)
            rs.set(self.name, f'{self.host}:{self.port}')
        except KeyboardInterrupt:
            pass
        finally:
            if RestfulDevice.dev.connected:
                RestfulDevice.dev.disconnect()
            rs.delete(self.name)
