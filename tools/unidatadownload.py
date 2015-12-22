"""Download Unicodedata files."""
from __future__ import unicode_literals
import sys
import unicodedata
import os

__version__ = '1.0.0'

PY3 = sys.version_info >= (3, 0) and sys.version_info[0:2] < (4, 0)

if PY3:
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

home = os.path.dirname(os.path.abspath(__file__))


def download_unicodedata(output):
    """Download unicode data scripts and blocks."""
    files = ('Blocks.txt', 'Scripts.txt')
    version = unicodedata.unidata_version
    url = 'http://www.unicode.org/Public/%s/ucd/' % version

    destination = os.path.join(output, 'unicodedata', version)
    if not os.path.exists(destination):
        os.makedirs(destination)
    for f in files:
        furl = url + f
        file_location = os.path.join(destination, f)
        print('Downloading: %s --> %s' % (furl, file_location))
        response = urlopen(furl)
        data = response.read()
        with open(file_location, 'w') as uf:
            uf.write(data.decode('utf-8'))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='unipropgen', description='Generate a unicode property table.')
    parser.add_argument('--version', action='version', version="%(prog)s " + __version__)
    parser.add_argument('--output', default=home, help='Output file.')
    args = parser.parse_args()

    download_unicodedata(args.output)
