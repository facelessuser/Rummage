import gettext

lang = None
_ = None


def setup(domain, pth, language=None):
    """
    Setup a language
    """

    global _
    global lang
    if language is not None:
        try:
            lang = gettext.translation(domain, pth, languages=[language])
            lang.install(unicode=True)
            _ = lambda t: lang.ugettext(t)
        except:
            _default_setup()
    else:
        _default_setup()


def _default_setup():
    """
    Default configuration (just pass the string back)
    """

    global _
    global lang
    lang = None
    _ = lambda t: t


def get(t):
    return _(t)


# Init ot default setup on intitial load
_default_setup()
