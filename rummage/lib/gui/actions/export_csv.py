"""Export CSV."""
import time
import codecs
import subprocess
from ..localization import _
from .. import util
from ... import rumcore

if util.platform() == "windows":
    from os import startfile

RESULT_ROW = '%(file)s,%(matches)s,%(extensions)s,%(size)s,%(path)s,%(encoding)s,%(modified)s,%(created)s\n'
RESULT_CONTENT_ROW = '%(file)s,%(line)s,%(matches)s,%(extensions)s,%(context)s\n'


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


def export_result_list(res, csv):
    """Export result list."""

    if len(res) == 0:
        return

    columns = (
        _('File'), _('Matches'), _('Extensions'), _('Size'), _('Path'), _('Encoding'), _('Modified'), _('Created')
    )
    result_table_header = ','.join([csv_encode(x) for x in columns]) + "\n"

    csv.write(result_table_header)

    for item in res.values():
        csv.write(
            RESULT_ROW % {
                "file": csv_encode(item[0]),
                "matches": csv_encode(util.to_ustr(item[1])),
                "extensions": csv_encode(item[2]),
                "size": csv_encode('%.2fKB' % item[3]),
                "path": csv_encode(item[4]),
                "encoding": csv_encode(item[5]),
                "modified": csv_encode(time.ctime(item[6])),
                "created": csv_encode(time.ctime(item[7]))
            }
        )

    csv.write("\n")


def export_result_content_list(res, csv):
    """Export result content list."""

    if len(res) == 0:
        return

    columns = (_('File'), _('Line'), _('Matches'), _('Extensions'), _('Context'))
    result_content_table_header = ','.join([csv_encode(x) for x in columns]) + "\n"

    csv.write(result_content_table_header)

    for item in res.values():
        csv.write(
            RESULT_CONTENT_ROW % {
                "file": csv_encode(item[0][0]),
                "line": csv_encode(util.to_ustr(item[1])),
                "matches": csv_encode(util.to_ustr(item[2])),
                "extensions": csv_encode(item[3]),
                "context": csv_encode(item[4])
            }
        )

    csv.write("\n")


def export(export_csv, chain, result_list, result_content_list):
    """Export results to CSV."""

    regex_search = csv_encode(_("Regex Search"))
    literal_search = csv_encode(_("Literal Search"))

    with codecs.open(export_csv, "w", encoding="utf-8-sig") as csv:
        for pattern, replace, flags in chain:
            csv.write(
                "%s,%s\n" % (
                    (literal_search if flags & rumcore.LITERAL else regex_search), csv_encode(pattern)
                )
            )
        csv.write('\n')
        export_result_list(result_list, csv)
        export_result_content_list(result_content_list, csv)

    platform = util.platform()
    if platform == "macos":
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
