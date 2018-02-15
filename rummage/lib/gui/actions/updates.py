"""Perform a check for latest versions on PyPI."""
from __future__ import unicode_literals
from ... import __version__
import json
import re
from urllib.request import urlopen

RE_VER = re.compile(r'(?P<major>\d+)\.(?P<minor>\d+)(?:\.(?P<micro>\d+))?(?:(?P<type>a|b|rc|post)(?P<pre_post>\d+))?')
releases = {"a": 'alpha', "b": 'beta', "rc": 'candidate', "post": 'final'}


def parse_version(ver, pre=False):
    """Parse version into a comparable tuple."""

    m = RE_VER.match(ver)
    # Post releases will be formatted like a normal release stripping of the post specifier
    # as post releases are essentially things like doc changes or things like that.
    rtype = releases[m.group('type')] if m.group('type') else 'final'

    if rtype in ('alpha', 'beta', 'candidate') and not pre:
        return (0, 0, 0, 'alpha', 0, 0)
    micro = int(m.group('micro')) if m.group('micro') else 0

    return (int(m.group('major')), int(m.group('minor')), micro, rtype, 0)


def check_update(pre=False):
    """Check for module update."""

    latest_ver_str = None
    url = 'http://pypi.python.org/pypi/rummage/json'
    try:
        response = urlopen(url, timeout=5)
        data = json.loads(response.read().decode('utf-8'))
        latest = (0, 0, 0, 'alpha', 0)
        latest_str = None
        for ver in data['releases'].keys():
            ver_info = parse_version(ver)
            if ver_info > latest:
                latest = ver_info
                latest_str = ver
        if __version__.version_info < latest:
            latest_ver_str = latest_str
    except Exception as e:
        pass
    return latest_ver_str
