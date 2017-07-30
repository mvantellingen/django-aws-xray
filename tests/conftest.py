import json
import attr
import socket
import threading
import pytest
import select
import queue

from django.conf import settings


def pytest_configure():
    settings.configure(
        MIDDLEWARE=[
            'django_aws_xray.middleware.XRayMiddleware'
        ],
        INSTALLED_APPS=[
            'django_aws_xray',
            'tests.app',
        ],
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'unique-snowflake',
            }
        },
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'db.sqlite',
            },
        },
        ROOT_URLCONF='tests.app.urls',
        AWS_XRAY_HOST='127.0.0.1',
        AWS_XRAY_PORT=2399,
    )


@attr.s
class XRayDaemon:
    messages = attr.ib(default=attr.Factory(queue.Queue))

    def get_new_messages(self):
        result = []
        while True:
            try:
                data = self.messages.get(block=True, timeout=0.200)
            except queue.Empty:
                break

            header, body = data.split(b'\n', 1)
            header = json.loads(header)
            body = json.loads(body)

            assert header == {
                'format': 'json',
                'version': 1
            }
            result.append(body)
        return result


@pytest.fixture
def xray_daemon():
    address = ('127.0.0.1', 2399)

    is_completed = threading.Event()
    is_running = threading.Event()
    daemon = XRayDaemon()

    def run():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(address)

        while True:
            is_running.set()
            ready = select.select([sock], [], [], 0.100)
            if ready[0]:
                data, addr = sock.recvfrom(64 * 1024)
                daemon.messages.put(data)

            if is_completed.is_set():
                break

    thread = threading.Thread(target=run)
    thread.start()

    if is_running.wait():
        yield daemon

    is_completed.set()
    thread.join()



