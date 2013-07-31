from time import ctime
from os import startfile
import codecs
import sys
import subprocess
from _lib.localization import get as _

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


def csv_encode(text):
    # Format text to HTML
    encode_table = {
        '"':  '""',
        '\n': '',
        '\r': ''
    }

    return '"%s"' % ''.join(
        encode_table.get(c, c) for c in text
    )


RESULT_ROW = '%(file)s,%(size)s,%(matches)s,%(path)s,%(encoding)s,%(modified)s,%(created)s\n'


RESULT_TABLE_HEADER = ','.join([csv_encode(x) for x in [_('File'), _('Size'), _('Matches'), _('Path'), _('Encoding'), _('Modified'), _('Created')]]) + "\n"


RESULT_CONTENT_ROW = '%(file)s,%(line)s,%(matches)s,%(context)s\n'


RESULT_CONTENT_TABLE_HEADER = ','.join([csv_encode(x) for x in [_('File'), _('Line'), _('Matches'), _('Context')]]) + "\n"


def export_result_list(res, csv):
    length = len(res)
    if length == 0:
        return

    csv.write(RESULT_TABLE_HEADER)

    for x in range(0, length):
        item = res[x]
        csv.write(
            RESULT_ROW % {
                "file": csv_encode(item[0]),
                "size": csv_encode('%.2fKB' % item[1]),
                "matches": csv_encode(str(item[2])),
                "path": csv_encode(item[3]),
                "encoding": csv_encode(item[4]),
                "modified": csv_encode(ctime(item[5])),
                "created": csv_encode(ctime(item[6]))
            }
        )

    csv.write("\n")


def export_result_content_list(res, csv):
    length = len(res)
    if length == 0:
        return

    csv.write(RESULT_CONTENT_TABLE_HEADER)

    for x in range(0, length):
        item = res[x]
        csv.write(
            RESULT_CONTENT_ROW % {
                "file": csv_encode(item[0][0]),
                "line": csv_encode(str(item[1])),
                "matches": csv_encode(str(item[2])),
                "context": csv_encode(item[3])
            }
        )

    csv.write("\n")


def export(export_csv, search, regex_search, result_list, result_content_list):

    with codecs.open(export_csv, "w", encoding="utf-8") as csv:
        csv.write(u'\uFEFF')
        search_expression = "%s,%s\n\n" % (csv_encode(_("Regex Search") if regex_search else _("Literal Search")), csv_encode(search))
        csv.write(search_expression)
        export_result_list(result_list, csv)
        export_result_content_list(result_content_list, csv)

    if _PLATFORM == "osx":
        subprocess.Popen(['open', csv.name])
    elif _PLATFORM == "windows":
        startfile(csv.name)
    else:
        try:
            # Maybe...?
            subprocess.Popen(['xdg-open', csv.name])
        except OSError:
            # Well we gave it our best...
            pass
