import threading
import time
import uuid
from contextlib import contextmanager

from django_aws_xray import records
from django_aws_xray.connection import Connection

tls = threading.local()
tls.trace_id = None
tls.current_trace = None


def set_current_trace(trace):
    tls.current_trace = trace


def get_current_trace():
    return getattr(tls, 'current_trace', None)


class Trace:

    def __init__(self, root, parent=None, sampled=None):
        self.root = root
        self.parent = parent
        self.sampled = sampled
        self._connection = Connection()
        self._segment_stack = list()
        self._segment_buffer = list()

    def send(self):
        if self.sampled:
            for record in self._segment_buffer:
                self._connection.send(record)
            self._segment_buffer.clear()

    @property
    def http_header(self):
        parts = [
            ('Root', self.root),
            ('Parent', self.parent),
            ('Sampled', '1' if self.sampled else None),
        ]
        return ';'.join('%s=%s' % (k, v) for k, v in parts if v is not None)

    @contextmanager
    def track(self, name):
        # Create the correct record type
        if len(self._segment_stack) == 0:
            record = records.SegmentRecord(
                name=name,
                trace_id=self.root)
        else:
            parent = self._segment_stack[-1]
            record = records.SubSegmentRecord(
                name=name,
                trace_id=self.root,
                parent_id=parent.id)

        # Push the record on our stack
        self._segment_stack.append(record)

        record.trace_id = self.root
        record.start_time = time.time()
        try:
            yield record
        finally:
            assert self._segment_stack.pop() is record
            record.end_time = time.time()
            self._segment_buffer.append(record)

    @classmethod
    def generate_new(cls, sampled=True):
        root = '1-%08x-%s' % (int(time.time()), uuid.uuid4().hex[:24])
        return cls(root=root, parent=None, sampled=sampled)

    @classmethod
    def from_http_header(cls, header_value, sampled):
        """

        Root=1-5759e988-bd862e3fe1be46a994272793;Parent=53995c3f42cd8ad8;Sampled=1

        """
        parts = header_value.lower().split(';')
        data = {
            'sampled': '1' if sampled else '0'
        }

        for part in parts:
            subparts = part.split('=', 1)
            if len(subparts) == 2:
                data[subparts[0]] = subparts[1]

        root = data.get('root')
        parent = data.get('parent')
        sampled = data.get('sampled') == '1'
        return cls(root=root, parent=parent, sampled=sampled)
