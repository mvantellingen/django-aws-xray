import uuid

import attr

from django_aws_xray.xray import connection


@attr.s
class SegmentRecord:
    id = attr.ib(init=False, default=attr.Factory(lambda: uuid.uuid4().hex[16:]))
    name = attr.ib()
    start_time = attr.ib()
    end_time = attr.ib()
    trace_id = attr.ib()
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

        # if self.subsegments:
        #     data['subsegments'] = [
        #         subsegment.serialize(skip_parent_id=True)
        #         for subsegment in self.subsegments
        #     ]

        return data

    def add_subsegment(self, subsegment):
        subsegment.trace_id = self.trace_id
        subsegment.parent_id = self.id
        connection.send(subsegment)


@attr.s
class SubSegmentRecord:
    id = attr.ib(init=False, default=attr.Factory(lambda: uuid.uuid4().hex[16:]))
    name = attr.ib()
    start_time = attr.ib()
    end_time = attr.ib()
    trace_id = attr.ib(default=None, init=False)
    parent_id = attr.ib(default=None, init=False)
    namespace = attr.ib(default='remote')
    subsegments = attr.ib(default=attr.Factory(list))
    http = attr.ib(default=None)
    sql = attr.ib(default=None)

    def serialize(self, skip_parent_id=False):
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

        if skip_parent_id:
            data['parent_id'] = None

        # if self.subsegments:
        #     data['subsegments'] = [
        #         subsegment.serialize(skip_parent_id=True)
        #         for subsegment in self.subsegments
        #     ]

        return data

    def add_subsegment(self, subsegment):
        subsegment.trace_id = self.trace_id
        subsegment.parent_id = self.id
        connection.send(subsegment)


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
