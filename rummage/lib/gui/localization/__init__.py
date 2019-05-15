"""Localization."""
import gettext
import os

lang = None
current_domain = None
locale_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')


def _(text):
    """Unicode `gettext`."""

    return lang.gettext(text) if lang is not None else text


def setup(domain, language=None):
    """Setup a language."""

    global lang
    global current_domain
    if language is not None:
        try:
            lang = gettext.translation(domain, locale_path, languages=[language])
            lang.install()
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


# Initialize the default setup on initial load
_default_setup()
