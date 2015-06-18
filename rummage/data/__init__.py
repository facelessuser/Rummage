"""Data resource lib."""
from __future__ import unicode_literals
import os
import codecs
from wx.lib.embeddedimage import PyEmbeddedImage
import base64

RESOURCE_PATH = os.path.abspath(os.path.dirname(__file__))


def get_file(file_name, raw=False):
    """Get the data file."""

    text = b'' if raw else ''
    resource = os.path.join(RESOURCE_PATH, file_name)
    if os.path.exists(resource):
        try:
            if raw:
                with open(resource, 'rb') as f:
                    text = f.read()
            else:
                with codecs.open(resource, 'r', encoding='utf-8') as f:
                    text = f.read()
        except Exception:
            pass
    return text


def get_image(file_name, b64=False):
    """Get the image as a PyEmbeddedImage."""
    icon = b''
    resource = os.path.join(RESOURCE_PATH, file_name)
    if os.path.exists(resource):
        try:
            with open(resource, "rb") as f:
                icon = base64.b64encode(f.read())
        except Exception:
            pass
    return PyEmbeddedImage(icon) if not b64 else unicode(icon)
