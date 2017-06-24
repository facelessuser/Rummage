"""Export CSV."""
from __future__ import unicode_literals
from time import ctime
import codecs
import subprocess
from ..localization import _
from .. import util

if util.platform() == "windows":
    from os import startfile


def csv_encode(text):
    """Format text for CSV."""

    encode_table = {
        '"': '""',
        '\n': '',
        '\r': ''
    }

    return '"%s"' % ''.join(
        encode_table.get(c, c) for c in text
    )


REGEX_SEARCH = csv_encode(_("Regex Search"))

LITERAL_SEARCH = csv_encode(_("Literal Search"))


RESULT_ROW = '%(file)s,%(size)s,%(matches)s,%(path)s,%(encoding)s,%(modified)s,%(created)s\n'


RESULT_TABLE_HEADER = ','.join(
    [csv_encode(x) for x in [_('File'), _('Size'), _('Matches'), _('Path'), _('Encoding'), _('Modified'), _('Created')]]
) + "\n"


RESULT_CONTENT_ROW = '%(file)s,%(line)s,%(matches)s,%(context)s\n'


RESULT_CONTENT_TABLE_HEADER = ','.join(
    [csv_encode(x) for x in [_('File'), _('Line'), _('Matches'), _('Context')]]
) + "\n"


def export_result_list(res, csv):
    """Export result list."""

    if len(res) == 0:
        return

    csv.write(RESULT_TABLE_HEADER)

    for item in res.values():
        csv.write(
            RESULT_ROW % {
                "file": csv_encode(item[0]),
                "size": csv_encode('%.2fKB' % item[1]),
                "matches": csv_encode(util.to_ustr(item[2])),
                "path": csv_encode(item[3]),
                "encoding": csv_encode(item[4]),
                "modified": csv_encode(ctime(item[5])),
                "created": csv_encode(ctime(item[6]))
            }
        )

    csv.write("\n")


def export_result_content_list(res, csv):
    """Export result content list."""

    if len(res) == 0:
        return

    csv.write(RESULT_CONTENT_TABLE_HEADER)

    for item in res.values():
        csv.write(
            RESULT_CONTENT_ROW % {
                "file": csv_encode(item[0][0]),
                "line": csv_encode(util.to_ustr(item[1])),
                "matches": csv_encode(util.to_ustr(item[2])),
                "context": csv_encode(item[3])
            }
        )

    csv.write("\n")


def export(export_csv, search, regex_search, result_list, result_content_list):
    """Export results to CSV."""

    with codecs.open(export_csv, "w", encoding="utf-8-sig") as csv:
        search_expression = "%s,%s\n\n" % ((REGEX_SEARCH if regex_search else LITERAL_SEARCH), csv_encode(search))
        csv.write(search_expression)
        export_result_list(result_list, csv)
        export_result_content_list(result_content_list, csv)

    platform = util.platform()
    if platform == "osx":
        subprocess.Popen(['open', csv.name])
    elif platform == "windows":
        startfile(csv.name)
    else:
        try:
            # Maybe...?
            subprocess.Popen(['xdg-open', csv.name])
        except OSError:
            # Well we gave it our best...
            pass
