from django.conf import settings

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

patches = getattr(settings, 'AWS_XRAY_PATCHES', [])

print(patches)

for patch in patches:
    import_module(patch).patch()
