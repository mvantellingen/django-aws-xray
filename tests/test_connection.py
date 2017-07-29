import time
from django_aws_xray import xray, records


def test_send(xray_daemon):

    record = records.SegmentRecord(
        name='test',
        start_time=1501314262.7056608,
        end_time=1501314262.901,
        trace_id='my-id')

    xray.connection.send(record)

    messages = xray_daemon.get_new_messages()
    assert len(messages) == 1
