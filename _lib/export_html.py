import webbrowser
import re
from time import ctime
from os.path import join
import codecs
import sys

from _3rdparty.sorttable.sorttable import sorttable as SORT_JS

from _gui.messages import filepickermsg

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


CSS_HTML = \
'''
/* Sortable tables */
table.sortable thead {
    background-color:#2b5b72;
    color:#eeeeee;
    font-weight: bold;
    cursor: default;
}
table.sortable {
    background: #ffffff;
}
table.sortable tbody tr:nth-child(2n) td {
  background: #eeeeee;
}
table.sortable tbody tr:nth-child(2n+1) td {
  background: #fffffff;
}
h1 {
    color: white;
}
/* Tab Bar */
#bar a{
    padding-top:10px;
    padding-left: 20px;
    padding-right: 20px;
    background:#397997;
    color:#eeeeee;
    text-decoration:none;
    font-weight:bold;
    -moz-border-radius-topright: 10px;
    border-top-right-radius: 10px;
    -moz-border-radius-topleft: 10px;
    border-top-left-radius: 10px;
    /*border-left: solid;*/
}
#bar a.unselected {
    background: #2b5b72;
}
#bar a:hover{
    color:#ccffff;
}
body {
    text-align: center;
    background: #6597ae;
}
table {
    border: 10px solid #397997;
    text-align: left;
    margin: auto;
    border-collapse: separate;
    -moz-border-radius: 10px;
    border-radius: 10px;
    -moz-border-radius: 10px;
    border-radius: 10px;
    border-spacing:0;
}
table td, table th {
    padding-left: 10px;
    padding-right: 10px;
}
div#bar {
    margin: auto;
}
div#main {
    width: 50%;
    margin: 0 auto;
}
'''

HTML_HEADER = \
'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<title>Export</title>
<style type="text/css">
%(css)s
</style>
<script type="text/javascript">
%(js)s
</script>
%(morejs)s
</head>
'''

RESULT_ROW = \
'''
<tr>
<td sorttable_customkey="%(file_sort)s">%(file)s</td>
<td sorttable_customkey="%(size_sort)s">%(size)s</td>
<td>%(matches)s</td>
<td>%(path)s</td>
<td>%(encoding)s</td>
<td sorttable_customkey="%(mod_sort)s">%(modified)s</td>
<td sorttable_customkey="%(cre_sort)s">%(created)s</td>
</tr>
'''

RESULT_TABLE_HEADER = \
'''
<tr>
<th>File</th>
<th>Size</th>
<th>Matches</th>
<th>Path</th>
<th>Encoding</th>
<th>Modified</th>
<th>Created</th>
</tr>
'''

RESULT_CONTENT_ROW = \
'''
<tr>
<td sorttable_customkey="%(file_sort)s">%(file)s</td>
<td>%(line)s</td>
<td>%(matches)s</td>
<td>%(context)s</td>
</tr>
'''

RESULT_CONTENT_TABLE_HEADER = \
'''
<tr>
<th>File</th>
<th>Line</th>
<th>Matches</th>
<th>Context</th>
</tr>
'''

TABS_START = \
'''
<div id="bar">
<a id="tabbutton1" href="javascript:select_tab(1)">Files</a>
<a id="tabbutton2" href="javascript:select_tab(2)">Content</a>
</div>

<div id="container">
<div class="main">
'''

TABS_END = \
'''
</div>
</div>
'''

LOAD_TAB = \
'''
<script type="text/javascript">
function select_tab(num) {
    var load_id = "tab" + num.toString();
    var other_id = (num == 1) ? "tab2" : "tab1";
    var load_button = "tabbutton" + num.toString();
    var other_button = (num == 1) ? "tabbutton2" : "tabbutton1";
    document.getElementById(other_id).style.display = "none";
    document.getElementById(load_id).style.display = "block";
    document.getElementById(load_button).className = "";
    document.getElementById(other_button).className = "unselected";
}
</script>
'''

TAB_INIT = \
'''
<script type="text/javascript">
select_tab(1)
</script>
'''

BODY_START = \
'''
<body>
<h1 id="title">Rummage Results</h1>
'''

BODY_END = \
'''
</body>
</html>
'''

def html_encode(text):
    # Format text to HTML
    encode_table = {
        '&':  '&amp;',
        '>':  '&gt;',
        '<':  '&lt;',
        '\t': ' ' * 4,
        '\n': '',
        '\r': ''
    }

    return re.sub(
        r'(?!\s($|\S))\s',
        '&nbsp;',
        ''.join(
            encode_table.get(c, c) for c in text
        ).encode('ascii', 'xmlcharrefreplace')
    )


def export_result_list(res, html):
    length = len(res)
    html.write('<div class="tab" id="tab1" style="display: block;">')
    html.write('<table class="sortable">')
    html.write(RESULT_TABLE_HEADER)

    for x in range(0, length):
        item = res[x]
        html.write(
            RESULT_ROW % {
                "file_sort": html_encode(join(item[3], item[0])),
                "file": html_encode(item[0]),
                "size_sort": str(item[1]),
                "size": '%.2fKB' % item[1],
                "matches": str(item[2]),
                "path": html_encode(item[3]),
                "encoding": item[4],
                "mod_sort": str(item[5]),
                "modified": ctime(item[5]),
                "cre_sort": str(item[6]),
                "created": ctime(item[6])
            }
        )
    html.write('</table>')
    html.write('</div>')


def export_result_content_list(res, html):
    length = len(res)
    html.write('<div class="tab" id="tab2" style="display: block;">')
    html.write('<table class="sortable">')
    html.write(RESULT_CONTENT_TABLE_HEADER)

    for x in range(0, length):
        item = res[x]
        html.write(
            RESULT_CONTENT_ROW % {
                "file_sort": html_encode(join(item[0][1], item[0][0])),
                "file": html_encode(item[0][0]),
                "line": str(item[1]),
                "matches": str(item[2]),
                "context": html_encode(item[3])
            }
        )
    html.write('</table>')
    html.write('</div>')


def export(result_list, result_content_list):
    export_html = filepickermsg("Export to...", "*.html", True)
    if export_html is None:
        return

    with codecs.open(export_html, "w", encoding="utf-8") as html:
        html.write(
            HTML_HEADER % {
                "js": SORT_JS,
                "morejs": LOAD_TAB,
                "css": CSS_HTML
            }
        )
        html.write(BODY_START)
        html.write(TABS_START)
        export_result_list(result_list, html)
        export_result_content_list(result_content_list, html)
        html.write(TABS_END)
        html.write(TAB_INIT)
        html.write(BODY_END)

    if _PLATFORM == "osx":
        import subprocess
        subprocess.Popen(['open', html.name])
    else:
        webbrowser.open(html.name, new=2)
