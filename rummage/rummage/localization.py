"""Localization."""
from __future__ import unicode_literals
import gettext
import sys

lang = None
current_domain = None

PY3 = (3, 0) <= sys.version_info < (4, 0)


def _(text):
    """Unicode gettext."""

    if lang is not None:
        text = lang.gettext(text)
    return text.decode("utf-8") if not isinstance(text, (str if PY3 else unicode)) else text


def setup(domain, pth, language=None):
    """Setup a language."""

    global lang
    global current_domain
    if language is not None:
        try:
            lang = gettext.translation(domain, pth, languages=[language])
            lang.install(unicode=True)
            current_domain = domain
        except Exception:
            _default_setup()
    else:
        _default_setup()


def _default_setup():
    """Default configuration (just pass the string back)."""

    global lang
    global current_domain
    lang = None
    current_domain = "en_US"


def get_current_domain():
    """Get the current domain."""

    return current_domain


# Init the default setup on intitial load
_default_setup()
