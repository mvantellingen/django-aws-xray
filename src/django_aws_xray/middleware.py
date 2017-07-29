import logging
import random
import time
import uuid

from django.conf import settings

from django_aws_xray import records, xray


class XRayMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.sampling_rate = getattr(settings, 'AWS_XRAY_SAMPLING_RATE', 100)
        self.exclude_paths = getattr(settings, 'AWS_XRAY_EXCLUDE_PATHS', [])
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        enable_tracing = random.randint(0, 100) <= self.sampling_rate
        for path in self.exclude_paths:
            if path.startswith(request.path):
                enable_tracing = False

        self.logger.info("Tracing enabled: %s", enable_tracing)

        if enable_tracing:
            trace = self._create_new_segment(request)
            xray.set_current_trace(trace)

        try:
            response = self.get_response(request)
            if enable_tracing:
                trace.http.response_status_code = response.status_code
            return response
        finally:
            if enable_tracing:
                trace.end_time = time.time()
                xray.connection.send(trace)
                xray.set_current_trace(None)

    def _create_new_segment(self, request):
        trace_id = request.META.get('HTTP_X_AMZN_TRACE_ID')
        http_data = None
        if trace_id:
            prefix, trace_id = trace_id.split('=', 1)
        else:
            trace_id = '1-%08x-%s' % (int(time.time()), uuid.uuid4().hex[:24])

        http_data = records.HttpRecord(
            request_method=request.method,
            request_url=request.get_full_path(),
            request_user_agent=request.META.get('User-Agent'))

        segment = records.SegmentRecord(
            name='django.request',
            start_time=time.time(),
            end_time=None,
            trace_id=trace_id,
            http=http_data)

        return segment
