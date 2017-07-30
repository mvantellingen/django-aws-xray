import wrapt

from django_aws_xray.traces import trace_http


def patched_render(func, instance, args, kwargs):
    name = 'django.template'

    with trace_http(name, 'render', instance.name):
        return func(*args, **kwargs)


def patch():
    wrapt.wrap_function_wrapper(
        'django.template', 'Template.render', patched_render)
