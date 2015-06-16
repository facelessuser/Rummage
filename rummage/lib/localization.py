"""Localization."""
import gettext

lang = None
_ = None
current_domain = None


def unicode_gettext(l, text):
    """Unicode gettext."""

    if l is not None:
        text = l.gettext(text)
    return text.decode("utf-8") if not isinstance(text, unicode) else text


def setup(domain, pth, language=None):
    """Setup a language."""

    global _
    global lang
    global current_domain
    if language is not None:
        try:
            lang = gettext.translation(domain, pth, languages=[language])
            lang.install(unicode=True)
            _ = lambda t, lang=lang: unicode_gettext(lang, t)
            current_domain = domain
        except:
            _default_setup()
    else:
        _default_setup()


def _default_setup():
    """Default configuration (just pass the string back)."""

    global _
    global lang
    global current_domain
    lang = None
    _ = lambda t: unicode_gettext(None, t)
    current_domain = "en_US"


def get(t):
    """Get the translated string."""

    return _(t)


def get_current_domain():
    """Get the current domain."""

    return current_domain


# Init the default setup on intitial load
_default_setup()
