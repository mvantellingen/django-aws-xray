from contextlib import contextmanager

from django_aws_xray import records, xray

MAX_SQL_QUERY_LENGTH = 8192


@contextmanager
def trace(name):
    trace = xray.get_current_trace()
    if trace:
        with trace.track(name):
            yield
    else:
        yield


@contextmanager
def trace_sql(name, db, query):
    sql_record = records.SqlRecord(
        sanitized_query=query.strip()[:MAX_SQL_QUERY_LENGTH],
        database_type=db.vendor)

    trace = xray.get_current_trace()
    if trace:
        with trace.track(name) as record:
            record.sql = sql_record
            yield sql_record
    else:
        yield sql_record


@contextmanager
def trace_http(name, method, url):
    http_record = records.HttpRecord(
        request_method=method,
        request_url=url)

    trace = xray.get_current_trace()
    if trace:
        with trace.track(name) as record:
            record.http = http_record
            yield http_record
    else:
        yield http_record
