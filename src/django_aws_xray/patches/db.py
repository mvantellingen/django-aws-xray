import wrapt

from django_aws_xray.traces import trace_sql


def key(db, attr):
    return 'db.%s.%s.%s' % (db.client.executable_name, db.alias, attr)


def _get_query_type(query):
    return (query.split(None, 1) or ['__empty__'])[0].lower()


def patched_execute(func, instance, args, kwargs):
    query = args[0]
    name = key(instance.db, 'execute.%s' % _get_query_type(query))
    with trace_sql(name, instance.db, query):
        return func(*args, **kwargs)


def patched_executemany(func, instance, args, kwargs):
    query = args[0]
    name = key(instance.db, 'executemany.%s' % _get_query_type(query))
    with trace_sql(name, instance.db, query):
        return func(*args, **kwargs)


def patched_callproc(func, instance, args, kwargs):
    query = args[0]
    name = key(instance.db, 'callproc.%s' % _get_query_type(query))
    with trace_sql(name, instance.db, query):
        return func(*args, **kwargs)


def patch():
    wrapt.wrap_function_wrapper(
        'django.db.backends.utils', 'CursorWrapper.execute', patched_execute)
    wrapt.wrap_function_wrapper(
        'django.db.backends.utils', 'CursorWrapper.executemany', patched_executemany)
    wrapt.wrap_function_wrapper(
        'django.db.backends.utils', 'CursorWrapper.callproc', patched_callproc)
