import wrapt

from django_aws_xray.traces import trace_http


def patched_request(func, instance, args, kwargs):
    method = kwargs.get('method') or args[0]
    url = kwargs.get('url') or args[1]
    name = 'requests.request'

    with trace_http(name, method, url) as trace:
        response = func(*args, **kwargs)
        trace.response_status_code = response.status_code
        return response


def patch():
    """ Monkeypatch the requests library to trace http calls. """
    wrapt.wrap_function_wrapper('requests', 'Session.request', patched_request)
