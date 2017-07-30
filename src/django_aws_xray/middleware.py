import logging
import random
import time

from django.conf import settings

from django_aws_xray import records, xray


class XRayMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.sampling_rate = getattr(settings, 'AWS_XRAY_SAMPLING_RATE', 100)
        self.exclude_paths = getattr(settings, 'AWS_XRAY_EXCLUDE_PATHS', [])
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        trace = self._create_trace(request)

        # Set the thread local trace object
        xray.set_current_trace(trace)

        with trace.track('django.request') as record:
            response = self.get_response(request)
            record.http = self._create_http_record(request, response)

        # Send out the traces
        trace.send()

        # Set the HTTP header
        response['X-Amzn-Trace-Id'] = trace.http_header

        # Cleanup the thread local trace object
        xray.set_current_trace(None)

        return response

    def _create_trace(self, request):
        # Decide if we need to sample this request
        sampled = random.randint(0, 100) <= self.sampling_rate
        for path in self.exclude_paths:
            if request.path.startswith(path):
                sampled = False

        trace_header = request.META.get('HTTP_X_AMZN_TRACE_ID')
        if trace_header:
            trace = xray.Trace.from_http_header(trace_header, sampled)
        else:
            trace = xray.Trace.generate_new(sampled)

        return trace

    def _create_http_record(self, request, response):
        return records.HttpRecord(
            request_method=request.method,
            request_url=request.get_full_path(),
            request_user_agent=request.META.get('User-Agent'),
            response_status_code=response.status_code)
