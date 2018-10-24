"""Perform a check for latest versions on PyPI."""
from __future__ import unicode_literals
from ... import __meta__
import json
import re
from urllib.request import urlopen

RE_VER = re.compile(
    r'''(?x)
    (?P<major>\d+)\.(?P<minor>\d+)(?:\.(?P<micro>\d+))?
    (?:(?P<type>a|b|rc)(?P<pre>\d+))?
    (?:\.post(?P<post>\d+))?
    (?:\.dev(?P<dev>\d+))?
    '''
)
releases = {"a": 'alpha', "b": 'beta', "rc": 'candidate'}


def parse_version(ver, pre=False):
    """Parse version into a comparable tuple."""

    m = RE_VER.match(ver)
    # Post releases will be formatted like a normal release stripping of the post specifier
    # as post releases are essentially things like doc changes or things like that.
    rtype = releases[m.group('type')] if m.group('type') else 'final'
    # Development release should never actually be on the server,
    # but if it was, adjust the type to a development type.
    if m.group('dev'):
        rtype = '.dev-' + rtype

    # Ignore development releases and prereleases.
    if rtype.startswith('.dev') or (rtype in ('alpha', 'beta', 'candidate') and not pre):
        return (0, 0, 0, 'alpha', 0, 0)
    micro = int(m.group('micro')) if m.group('micro') else 0

    return (int(m.group('major')), int(m.group('minor')), micro, rtype, 0)


def check_update(pre=False):
    """Check for module update."""

    latest_ver_str = None
    url = 'https://pypi.python.org/pypi/rummage/json'
    response = urlopen(url, timeout=5)
    data = json.loads(response.read().decode('utf-8'))
    latest = (0, 0, 0, 'alpha', 0)
    latest_str = None
    for ver in data['releases'].keys():
        ver_info = parse_version(ver)
        if ver_info > latest:
            latest = ver_info
            latest_str = ver
    if __meta__.__version_info__ < latest:
        latest_ver_str = latest_str

    return latest_ver_str
