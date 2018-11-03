from flask import Flask, url_for

from flask_restful import reqparse, abort, Api, Resource
import argparse
import sys
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
                else:
                    resp = f'No attribute named {ep}'
                return {ep: resp}
                
            def put(self, ep):
                if ep in self.dev.public:
                    args = rparser.parse_args()
                    val = args['value']
                    try:
                        setattr(self.dev, ep, val)
                        resp = f'{ep} set to {val}'
                    except:
                        resp = f'{ep} is not writable.'
                else:
                    resp = f'No attribute named {ep}'        
                return {ep: resp}, 201

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
