import wrapt

from django_aws_xray.traces import trace_http


def patched_execute_command(func, instance, args, kwargs):

    # TODO: Metadata / Annotations
    # instance.connection_pool.connection_kwargs['host']
    # instance.connection_pool.connection_kwargs['db']

    command = args[0]
    key = None
    if command in ('GET', 'SET', 'DELETE', 'INCR', 'DECR'):
        key = str(args[1])

    with trace_http('redis', command, key):
        response = func(*args, **kwargs)
        return response


def patch():
    """ Monkeypatch the requests library to trace http calls. """
    try:
        wrapt.wrap_function_wrapper(
            'redis.client', 'Redis.execute_command', patched_execute_command)
        wrapt.wrap_function_wrapper(
            'redis.client', 'StrictRedis.execute_command', patched_execute_command)
    except ModuleNotFoundError:
        pass
