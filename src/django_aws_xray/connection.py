import json
import socket

from django.conf import settings


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
