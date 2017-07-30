from django_aws_xray import xray, records


def test_trace_from_http_header_root():
    header_value = 'Root=1-5759e988-bd862e3fe1be46a994272793'
    trace_object = xray.Trace.from_http_header(header_value, sampled=True)
    assert trace_object.root == '1-5759e988-bd862e3fe1be46a994272793'
    assert trace_object.parent is None
    assert trace_object.sampled is True


def test_trace_from_http_header_root_force_sampled():
    header_value = 'Root=1-5759e988-bd862e3fe1be46a994272793;Sampled=1'
    trace_object = xray.Trace.from_http_header(header_value, sampled=False)
    assert trace_object.root == '1-5759e988-bd862e3fe1be46a994272793'
    assert trace_object.parent is None
    assert trace_object.sampled is True


def test_trace_from_http_header_parent():
    header_value = 'Root=1-5759e988-bd862e3fe1be46a994272793;Parent=53995c3f42cd8ad8'
    trace_object = xray.Trace.from_http_header(header_value, sampled=True)
    assert trace_object.root == '1-5759e988-bd862e3fe1be46a994272793'
    assert trace_object.parent == '53995c3f42cd8ad8'
    assert trace_object.sampled is True


def test_trace_from_http_header_parent_force_sampled():
    header_value = 'Root=1-5759e988-bd862e3fe1be46a994272793;Parent=53995c3f42cd8ad8;Sampled=1'
    trace_object = xray.Trace.from_http_header(header_value, sampled=False)
    assert trace_object.root == '1-5759e988-bd862e3fe1be46a994272793'
    assert trace_object.parent == '53995c3f42cd8ad8'
    assert trace_object.sampled is True


def test_trace_from_http_header_errors():
    header_value = 'Root=1-5759e988-bd862e3fe1be46a994272793;Onzin;;;===;'
    trace_object = xray.Trace.from_http_header(header_value, sampled=True)
    assert trace_object.root == '1-5759e988-bd862e3fe1be46a994272793'
    assert trace_object.parent is None
    assert trace_object.sampled is True


def test_trace_stack():
    trace = xray.Trace.generate_new()

    record = records.SegmentRecord(name='root')

    with trace.track(record):
        assert len(trace._segment_stack) == 1

        subrecord = records.SubSegmentRecord(name='subitem')
        with trace.track(subrecord):
            assert len(trace._segment_stack) == 2

        assert len(trace._segment_stack) == 1
