"""Perform a check for latest versions on PyPI."""
from ... import __meta__
import json
from urllib.request import urlopen


def parse_version(ver, pre=False):
    """Parse version into a comparable tuple."""

    v = __meta__.parse_version(ver)

    # If this is a dev build, or pre release and we are not allowing them
    # generate a version which will be less than any version it is compared to.
    if v._is_dev() or (v._is_pre() and not pre):
        # Create a version which is before all versions.
        v = __meta__.Version(0, 0, 0, '.dev')

    # Exclude post number in comparison as they are not significant enough to alert the user.
    if v._is_post():
        v = __meta__.Version(*v[:4])

    return v


def check_update(pre=False):
    """Check for module update."""

    latest_ver_str = None
    url = 'https://pypi.python.org/pypi/rummage/json'
    response = urlopen(url, timeout=5)
    data = json.loads(response.read().decode('utf-8'))
    latest = (0, 0, 0, '.', 0)
    latest_str = None
    for ver in data['releases'].keys():
        ver_info = parse_version(ver)
        if ver_info > latest:
            latest = ver_info
            latest_str = ver
    if __meta__.__version_info__ < latest:
        latest_ver_str = latest_str

    return latest_ver_str
