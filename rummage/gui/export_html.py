"""Export HTML."""
import webbrowser
import re
from time import ctime
from os.path import join
import codecs
import base64
import subprocess
import sys
from ..icons.rum_ico import rum_64
from ..icons.glass import glass
from ..sorttable.sorttable import sorttable
from ..lib.localization import get as _
from ..lib.localization import get_current_domain

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


def html_encode(text):
    """Format text for HTML."""

    encode_table = {
        '&': '&amp;',
        '>': '&gt;',
        '<': '&lt;',
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


CSS_HTML = '''
body {
    padding: 0;
    margin: 0;
    height: auto;
    background: #28343b;
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHgAAAB4CAIAAAC2BqGFAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3QcaAhwIBNjPuwAAAn1JREFUeNrt3E1qw0AMhuGpKKUEArlVz9Ab9PiBQCili24CJsGxNfr5Nn1nPRLiYRhLJs7Lx+fXKFq/P99Dsg7HU1Wq6+WsqdlQFqzXt3dDWaBcc6JR3lUugEbZo5yFRtmpnIJG2a8ch0Z5SjkIjfKscgQa5YDyNDTKMeU5aJTDyhPQKGeUvdAoJ5Vd0CjnlfehUS5R3oFGuUp5CxrlQuWn0CjXKq9Do1yuvAKNcofyIzTKTcp30Cj3KS/QKLcq36BR7lYeYxjKAuVR+AMalLdnbENZoKw40Sgrrg6UFXc0yoqHIcqKrgNlRXuHsqKPRlkxsKCsmAxRVozgKCvedaDs2WYoC5Sz0Cj7NxvKAuU4NMqzIYayQDkCjXIs0FAWKM9Bo5wJN5QFyl5olPNJDGWB8j40ylWpDGWB8hY0yrW1GcoC5XVolDsqNJQFyo/QKPfVaSgLlBdolLurNZQ13zwYypqaDWXBOhxPhrJAueZEo7yrXACNskc5C42yUzkFjbJfOQ6N8pRyEBrlWeUINMoB5WlolGPKc9Aoh5UnoFHOKHuhUU4qu6BRzivvQ6NcorwDjXKV8hY0yoXKT6FRrlVeh0a5XHkFGuUO5UdolJuU76BR7lNeoFFuVb5Bo9ytPMYwlAXKQ/bfpP9c+Xo5G8oCZcWJRllxdaCsuKNRVjwMUVZ0HSgr2juUFX00yoqBBWXFZIiyYgRHWfGuA2XPNkNZoJyFRtm/2VAWKMehUZ4NMZQFyhFolGOBhrJAeQ4a5Uy4oSxQ9kKjnE9iKAuU96FRrkplKAuUt6BRrq3NUBYor0Oj3FGhoSxQfoRGua9OQ1mgvECj3F2toaz55uEPVbjSBFmfMz0AAAAASUVORK5CYII=');
    font-family:Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New, monospace;
    text-align: center;
}
h1 {
    position: relative;
    top: 0;
    margin-top: 0;
    padding-top: 50px;
    color: white;
    text-shadow: 2px 2px #333333;
}
#search_label {
    color: white;
}
img {
    padding: 0;
    border: 0;
    vertical-align: middle;
    width:32px;
    height: auto;
}
/* Sortable tables */
table.sortable thead {
    background-color:#2b5b72; /* Old browsers */
    background: -moz-linear-gradient(top,  #c5deea 0%, #397997 31%, #2b5b72 100%); /* FF3.6+ */
    background: -webkit-gradient(linear, left top, left bottom, color-stop(0%,#c5deea), color-stop(31%,#397997), color-stop(100%,#2b5b72)); /* Chrome,Safari4+ */
    background: -webkit-linear-gradient(top,  #c5deea 0%,#397997 31%,#2b5b72 100%); /* Chrome10+,Safari5.1+ */
    background: -o-linear-gradient(top,  #c5deea 0%,#397997 31%,#2b5b72 100%); /* Opera 11.10+ */
    background: -ms-linear-gradient(top,  #c5deea 0%,#397997 31%,#2b5b72 100%); /* IE10+ */
    background: linear-gradient(to bottom,  #c5deea 0%,#397997 31%,#2b5b72 100%); /* W3C */
    filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#c5deea', endColorstr='#2b5b72',GradientType=0 ); /* IE6-9 */
    padding-top: 5px;
    padding-bottom: 5px;
    text-shadow: 2px 2px #333333;
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
  background: #ffffff;
}
/* Tab Bar */
#bar a{
    margin: 0px;
    padding-top:5px;
    padding-left: 20px;
    padding-right: 20px;
    padding-bottom: 5px;
    color:#eeeeee;
    text-decoration:none;
    font-weight:bold;
    -moz-border-radius-topright: 10px;
    border-top-right-radius: 10px;
    -moz-border-radius-topleft: 10px;
    border-top-left-radius: 10px;
    border-bottom: 5px;
    text-shadow: 2px 2px #333333;
    background:#397997; /* Old browsers */
    background: -moz-linear-gradient(top,  #ffffff 1%, #6597ae 5%, #397997 100%); /* FF3.6+ */
    background: -webkit-gradient(linear, left top, left bottom, color-stop(1%,#ffffff), color-stop(5%,#6597ae), color-stop(100%,#397997)); /* Chrome,Safari4+ */
    background: -webkit-linear-gradient(top,  #ffffff 1%,#6597ae 5%,#397997 100%); /* Chrome10+,Safari5.1+ */
    background: -o-linear-gradient(top,  #ffffff 1%,#6597ae 5%,#397997 100%); /* Opera 11.10+ */
    background: -ms-linear-gradient(top,  #ffffff 1%,#6597ae 5%,#397997 100%); /* IE10+ */
    background: linear-gradient(to bottom,  #ffffff 1%,#6597ae 5%,#397997 100%); /* W3C */
    filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#ffffff', endColorstr='#397997',GradientType=0 ); /* IE6-9 */
    -moz-box-shadow: 3px 3px 4px #444;
    -webkit-box-shadow: 3px 3px 4px #444;
    box-shadow: 3px 3px 4px #444;
    -ms-filter: "progid:DXImageTransform.Microsoft.Shadow(Strength=4, Direction=135, Color='#444444')";
    filter: progid:DXImageTransform.Microsoft.Shadow(Strength=4, Direction=135, Color='#444444');
}
#bar a.unselected {
    background: #2b5b72; /* Old browsers */
    background: -moz-linear-gradient(top,  #ffffff 1%, #397997 5%, #2b5b72 100%); /* FF3.6+ */
    background: -webkit-gradient(linear, left top, left bottom, color-stop(1%,#ffffff), color-stop(5%,#397997), color-stop(100%,#2b5b72)); /* Chrome,Safari4+ */
    background: -webkit-linear-gradient(top,  #ffffff 1%,#397997 5%,#2b5b72 100%); /* Chrome10+,Safari5.1+ */
    background: -o-linear-gradient(top,  #ffffff 1%,#397997 5%,#2b5b72 100%); /* Opera 11.10+ */
    background: -ms-linear-gradient(top,  #ffffff 1%,#397997 5%,#2b5b72 100%); /* IE10+ */
    background: linear-gradient(to bottom,  #ffffff 1%,#397997 5%,#2b5b72 100%); /* W3C */
    filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#ffffff', endColorstr='#2b5b72',GradientType=0 ); /* IE6-9 */
}
#bar a:hover{
    color:#ccffff;
}
table {
    position: relative;
    z-index: 99;
    font-size: small;
    border: 8px solid #397997;
    text-align: left;
    margin: auto;
    border-collapse: separate;
    -moz-border-radius: 10px;
    border-radius: 10px;
    -moz-border-radius: 10px;
    border-radius: 10px;
    border-spacing:0;
    -moz-box-shadow: 3px 3px 4px #444;
    -webkit-box-shadow: 3px 3px 4px #444;
    box-shadow: 3px 3px 4px #444;
    -ms-filter: "progid:DXImageTransform.Microsoft.Shadow(Strength=4, Direction=135, Color='#444444')";
    filter: progid:DXImageTransform.Microsoft.Shadow(Strength=4, Direction=135, Color='#444444');
}
table td, table th {
    padding-left: 10px;
    padding-right: 10px;
}

dif.tab_hidden:after {
    visibility: hidden;
}

div.tab_hidden {
    display: none;
}
div#bar {
    margin: auto;
}
div.main {
    zoom: 1;
    padding-bottom: 50px;
}

'''  # noqa

TITLE = html_encode(_("Rummage Results"))

HTML_HEADER = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<META HTTP-EQUIV="Content-Language" Content="%(lang)s">
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<link rel="icon" type"image/png" href="data:image/png;base64,%(icon)s"/>
<title>%(title)s</title>
<style type="text/css">
%(css)s
</style>
<script type="text/javascript">
%(js)s
</script>
%(morejs)s
</head>
'''

RESULT_ROW = '''
<tr>
<td>%(file)s</td>
<td sorttable_customkey="%(size_sort)s">%(size)s</td>
<td>%(matches)s</td>
<td>%(path)s</td>
<td>%(encoding)s</td>
<td sorttable_customkey="%(mod_sort)s">%(modified)s</td>
<td sorttable_customkey="%(cre_sort)s">%(created)s</td>
</tr>
'''

RESULT_TABLE_HEADER = '''
<tr>
<th>%(file)s</th>
<th>%(size)s</th>
<th>%(matches)s</th>
<th>%(path)s</th>
<th>%(encoding)s</th>
<th>%(modified)s</th>
<th>%(created)s</th>
</tr>
''' % {
    "file": html_encode(_("File")),
    "size": html_encode(_("Size")),
    "matches": html_encode(_("Matches")),
    "path": html_encode(_("Path")),
    "encoding": html_encode(_("Encoding")),
    "modified": html_encode(_("Modified")),
    "created": html_encode(_("Created"))
}

RESULT_CONTENT_ROW = '''
<tr>
<td sorttable_customkey="%(file_sort)s">%(file)s</td>
<td>%(line)s</td>
<td>%(matches)s</td>
<td>%(context)s</td>
</tr>
'''

RESULT_CONTENT_TABLE_HEADER = '''
<tr>
<th>%(file)s</th>
<th>%(line)s</th>
<th>%(matches)s</th>
<th>%(context)s</th>
</tr>
''' % {
    "file": html_encode(_("File")),
    "line": html_encode(_("Line")),
    "matches": html_encode(_("Matches")),
    "context": html_encode(_("Context"))
}

FILES = html_encode(_("Files"))
CONTENT = html_encode(_("Content"))

TABS_START = '''
<div id="bar">
<a id="tabbutton1" href="javascript:select_tab(1)">%(file_tab)s</a>
<a id="tabbutton2" href="javascript:select_tab(2)">%(content_tab)s</a>
</div>

<div class="main">
'''

TABS_START_SINGLE = '''
<div id="bar">
<a id="tabbutton1" href="javascript:select_tab(1)">%(file_tab)s</a>
</div>

<div class="main">
'''

SEARCH_LABEL_REGEX = html_encode(_("Regex search:"))

SEARCH_LABEL_LITERAL = html_encode(_("Literal search:"))

TABS_END = '''
<label id="search_label">%(label)s %(search)s</label>
</div>
'''

LOAD_TAB = '''
<script type="text/javascript">
function select_tab(num) {
    var load_id = "tab" + num.toString();
    var other_id = (num == 1) ? "tab2" : "tab1";
    var load_button = "tabbutton" + num.toString();
    var other_button = (num == 1) ? "tabbutton2" : "tabbutton1";
    document.getElementById(load_id).className = "";
    document.getElementById(load_button).className = "";
    try {
        // In case there is only one tab catch if there is no other
        document.getElementById(other_id).className = "tab_hidden";
        document.getElementById(other_button).className = "unselected";
    } catch (err) {
        // pass
    }
}
</script>
'''

TAB_INIT = '''
<script type="text/javascript">
select_tab(1)
</script>
'''

BODY_START = '''
<body>
<h1 id="title"><img src="data:image/bmp;base64,%(icon)s"/>Rummage Results</h1>
'''

BODY_END = '''
</body>
</html>
'''


def export_result_list(res, html):
    """Export result list."""

    length = len(res)
    if length == 0:
        return
    html.write('<div id="tab1">')
    html.write('<table class="sortable">')
    html.write(RESULT_TABLE_HEADER)

    for x in range(0, length):
        item = res[x]
        html.write(
            RESULT_ROW % {
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
    """Export result content list."""

    length = len(res)
    if length == 0:
        return
    html.write('<div id="tab2"">')
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


def export(export_html, search, regex_search, result_list, result_content_list):
    """Export the results as HTML."""

    with codecs.open(export_html, "w", encoding="utf-8") as html:
        html.write(
            HTML_HEADER % {
                "js": sorttable,
                "morejs": LOAD_TAB,
                "css": CSS_HTML,
                "icon": base64.b64encode(glass.GetData()),
                "title": TITLE,
                "lang": get_current_domain()
            }
        )
        html.write(BODY_START % {"icon": base64.b64encode(rum_64.GetData())})
        html.write(
            (TABS_START if len(result_content_list) else TABS_START_SINGLE) % {
                "file_tab": FILES,
                "content_tab": CONTENT
            }
        )
        export_result_list(result_list, html)
        export_result_content_list(result_content_list, html)
        html.write(
            TABS_END % {
                "search": html_encode(search),
                "label": SEARCH_LABEL_REGEX if regex_search else SEARCH_LABEL_LITERAL
            }
        )
        html.write(TAB_INIT)
        html.write(BODY_END)

    if _PLATFORM == "osx":
        subprocess.Popen(['open', html.name])
    elif _PLATFORM == "windows":
        webbrowser.open(html.name, new=2)
    else:
        try:
            # Maybe...?
            subprocess.Popen(['xdg-open', html.name])
        except OSError:
            # Well we gave it our best...
            pass
