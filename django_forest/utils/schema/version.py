import sys

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata


def get_app_version():
    version = '0.0.0'
    try:
        version = metadata.version('django-forestadmin')
    except Exception:
        pass
    finally:
        return version
