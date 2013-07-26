from time import ctime
from os.path import join
import codecs
import sys
import subprocess

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


RESULT_ROW = u'''"%(file)s","%(size)s","%(matches)s","%(path)s","%(encoding)s","%(modified)s","%(created)s"\n'''


RESULT_TABLE_HEADER = u'''File,Size,Matches,Path,Encoding,Modified,Created\n'''


RESULT_CONTENT_ROW = '''"%(file)s","%(line)s","%(matches)s","%(context)s"\n'''


RESULT_CONTENT_TABLE_HEADER = '''File,Line,Matches,Context\n'''


def csv_encode(text):
    # Format text to HTML
    encode_table = {
        '"':  '""',
        '\n': '',
        '\r': ''
    }

    return ''.join(
        encode_table.get(c, c) for c in text
    )


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


def export(export_csv, result_list, result_content_list):

    with codecs.open(export_csv, "w", encoding="utf-8") as csv:
        export_result_list(result_list, csv)
        export_result_content_list(result_content_list, csv)

    if _PLATFORM == "osx":
        subprocess.Popen(['open', csv.name])
    elif _PLATFORM == "windows":
        os.startfile(csv.name)
    else:
        try:
            # Maybe...?
            subprocess.Popen(['xdg-open', csv.name])
        except OSError:
            # Well we gave it our best...
            pass
