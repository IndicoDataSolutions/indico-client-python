try:
    from importlib import metadata
except ImportError:
    # If running on pre-3.8
    import importlib_metadata as metadata


def get_version():
    return metadata.version("indico-client")
