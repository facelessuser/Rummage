"""Data resource lib."""
import os
import codecs

RESOURCE_PATH = os.path.abspath(os.path.dirname(__file__))


def get_file(file_name):
    """Get the data file."""

    text = ''
    resource = os.path.join(RESOURCE_PATH, file_name)
    if os.path.exists(resource):
        try:
            with codecs.open(resource, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception:
            pass
    return text
