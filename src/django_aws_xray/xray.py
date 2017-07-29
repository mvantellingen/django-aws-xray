import json
import socket
import threading

from django.conf import settings

tls = threading.local()
tls.trace_id = None
tls.current_trace = None


def set_current_trace(trace):
    tls.current_trace = trace


def get_current_trace():
    return getattr(tls, 'current_trace', None)


class Connection:

    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        hostname = getattr(settings, 'AWS_XRAY_HOST', '127.0.0.1')
        port = getattr(settings, 'AWS_XRAY_PORT', 2000)
        self._address = (hostname, port)

    def serialize(self, msg):
        data = '\n'.join([
            json.dumps({'format': 'json', 'version': 1}),
            json.dumps(msg.serialize())
        ])
        return data.encode('utf-8')

    def send(self, record):
        if not record:
            return

        data = self.serialize(record)
        self._socket.sendto(data, self._address)


connection = Connection()
