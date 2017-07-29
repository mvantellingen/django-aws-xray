from django_aws_xray.patches.utils import patch_method
from django_aws_xray.traces import trace_sql

try:
    from django.db.backends import utils as util
except ImportError:
    from django.db.backends import util


def key(db, attr):
    return 'db.%s.%s.%s' % (db.client.executable_name, db.alias, attr)


def _get_query_type(query):
    return (query.split(None, 1) or ['__empty__'])[0].lower()


def patched_execute(orig_execute, self, query, *args, **kwargs):
    name = key(self.db, 'execute.%s' % _get_query_type(query))
    with trace_sql(name, self.db, query):
        return orig_execute(self, query, *args, **kwargs)


def patched_executemany(orig_executemany, self, query, *args, **kwargs):
    name = key(self.db, 'executemany.%s' % _get_query_type(query))
    with trace_sql(name, self.db, query):
        return orig_executemany(self, query, *args, **kwargs)


def patched_callproc(orig_callproc, self, query, *args, **kwargs):
    name = key(self.db, 'callproc.%s' % _get_query_type(query))
    with trace_sql(name, self.db, query):
        return orig_callproc(self, query, *args, **kwargs)


def patch():
    """
    The CursorWrapper is a pretty small wrapper around the cursor.  If
    you are NOT in debug mode, this is the wrapper that's used.  Sadly
    if it's in debug mode, we get a different wrapper for version
    earlier than 1.6.
    """

    patch_method(util.CursorWrapper, 'execute')(patched_execute)
    patch_method(util.CursorWrapper, 'executemany')(patched_executemany)
    patch_method(util.CursorWrapper, 'callproc')(patched_callproc)
