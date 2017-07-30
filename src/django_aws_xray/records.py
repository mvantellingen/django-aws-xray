import uuid

import attr

from django_aws_xray.connection import Connection


@attr.s
class SegmentRecord:
    id = attr.ib(init=False, default=attr.Factory(lambda: uuid.uuid4().hex[16:]))
    name = attr.ib()
    trace_id = attr.ib(default=None)
    start_time = attr.ib(default=None)
    end_time = attr.ib(default=None)
    http = attr.ib(default=None)
    subsegments = attr.ib(default=attr.Factory(list))

    def serialize(self):
        data = {
            'name': self.name,
            'id': self.id,
            'start_time': self.start_time,
            'trace_id': self.trace_id,
            'end_time': self.end_time,
        }

        if self.http:
            data['http'] = self.http.serialize()

        return data


@attr.s
class SubSegmentRecord:
    id = attr.ib(init=False, default=attr.Factory(lambda: uuid.uuid4().hex[16:]))
    name = attr.ib()
    start_time = attr.ib(default=None)
    end_time = attr.ib(default=None)
    trace_id = attr.ib(default=None)
    parent_id = attr.ib(default=None)
    namespace = attr.ib(default='remote')
    subsegments = attr.ib(default=attr.Factory(list))
    http = attr.ib(default=None)
    sql = attr.ib(default=None)

    def serialize(self):
        data = {
            'name': self.name,
            'id': self.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'type': 'subsegment',
            'trace_id': self.trace_id,
            'parent_id': self.parent_id,
            'namespace': self.namespace,
        }

        if self.http:
            data['http'] = self.http.serialize()

        if self.sql:
            data['sql'] = self.sql.serialize()

        return data


@attr.s
class HttpRecord:
    request_method = attr.ib(default=None)
    request_url = attr.ib(default=None)
    request_user_agent = attr.ib(default=None)

    response_status_code = attr.ib(default=None)

    def serialize(self):
        return {
            'request': {
                'method': self.request_method,
                'url': self.request_url,
                'user_agent': self.request_user_agent,
            },
            'response': {
                'status': self.response_status_code
            }
        }


@attr.s
class SqlRecord:
    sanitized_query = attr.ib()
    database_type = attr.ib()

    def serialize(self):
        return {
            'sanitized_query': self.sanitized_query,
            'database_type': self.database_type,
        }
