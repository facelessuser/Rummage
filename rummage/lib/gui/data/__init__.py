"""Data resource library."""
import os
import codecs
import base64
from wx.lib.embeddedimage import PyEmbeddedImage
from .. import util
from ..util.rgba import RGBA  # noqa: F401
from ..util import images

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


def get_image(file_name, b64=False, tint=None, alpha=None):
    """Get the image as a `PyEmbeddedImage`."""
    icon = b''
    resource = os.path.join(RESOURCE_PATH, file_name)
    if os.path.exists(resource):
        try:
            with open(resource, "rb") as f:
                if tint:
                    icon = base64.b64encode(images.tint(f.read(), tint, alpha))
                elif alpha is not None:
                    icon = base64.b64encode(images.transparency(f.read(), alpha))
                else:
                    icon = base64.b64encode(f.read())
        except Exception:
            pass
    return PyEmbeddedImage(icon) if not b64 else util.to_ustr(icon)


def get_bitmap(file_name, tint=None, alpha=None):
    """
    Get bitmap.

    For retina, we provide images that are 2X size.
    We can't detect retina yet, so we use 2X for non retina as well.
    This works fine for macOS as it seems to scale the images to fit the sizer
    as long as you set the height and width of the bitmap object (not the actual data)
    to half size.

    Windows and Linux do not auto scale, so we have to actually scale them.
    In the future, we should load normal sizes for Windows/Linux (and macOS non retina if we can detect retina),
    and load a separate 2X size for macOS retina.  But this is an okay work around for now.
    """

    image = get_image(file_name, tint=tint, alpha=alpha).GetImage()
    scaled = image.Rescale(
        int(image.GetWidth() / 2),
        int(image.GetHeight() / 2)
    )
    bm = scaled.ConvertToBitmap()

    return bm
