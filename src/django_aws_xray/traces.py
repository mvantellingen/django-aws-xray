import time
from contextlib import contextmanager

from django_aws_xray import records, xray


@contextmanager
def trace(name, extra_data=None):
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()

        segment = xray.get_current_trace()
        if segment:
            record = records.SubSegmentRecord(
                name=name,
                start_time=start_time,
                end_time=end_time,
                **extra_data)
            segment.add_subsegment(record)


timer = trace


@contextmanager
def trace_sql(name, db, query):
    sql = records.SqlRecord(
        sanitized_query=query.strip(),
        database_type=db.vendor)
    with trace(name, extra_data={'sql': sql}):
        yield
