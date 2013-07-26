import webbrowser
import re
from time import ctime
from os.path import join
import codecs
import base64
import sys
from _icons.rum_ico import rum_64
from _icons.glass import glass

from sorttable.sorttable import sorttable as SORT_JS

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


CSS_HTML = \
'''
body {
    padding: 0;
    margin: 0;
    height: auto;
    background: #28343b;
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHgAAAB4CAIAAAC2BqGFAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3QcZFxghKl5cpgAAAoBJREFUeNrt3D1OxEAMhuHBNFRIlMBBch96Gm6ZgwDXoFkp2lU28fjna3inHlvWo9HEjjb78PH5NYrW98/vkKxlWapSreuqqdlQFqz3t1dDWaBcc6JRPlUugEbZo5yFRtmpnIJG2a8ch0Z5SjkIjfKscgQa5YDyNDTKMeU5aJTDyhPQKGeUvdAoJ5Vd0Cjnlc+hUS5RPoFGuUr5CBrlQuW70CjXKu9Do1yuvAONcofyLTTKTcpX0Cj3KW/QKLcqX6BR7lYeYxjKAuVR+AMalI9nbENZoKw40Sgrrg6UFXc0yoqHIcqKrgNlRXuHsqKPRlkxsKCsmAxRVozgKCvedaDs2WYoC5Sz0Cj7NxvKAuU4NMqzIYayQDkCjXIs0FAWKM9Bo5wJN5QFyl5olPNJDGWB8jk0ylWpDGWB8hE0yrW1GcoC5X1olDsqNJQFyrfQKPfVaSgLlDdolLurNZQ13zwYypqaDWXBWpbFUBYo15xolE+VC6BR9ihnoVF2KqegUfYrx6FRnlIOQqM8qxyBRjmgPA2Nckx5DhrlsPIENMoZZS80ykllFzTKeeVzaJRLlE+gUa5SPoJGuVD5LjTKtcr70CiXK+9Ao9yhfAuNcpPyFTTKfcobNMqtyhdolLuVxxiPT88vKHcrD9l/k/5z5XVdDWWBsuJEo6y4OlBW3NEoKx6GKCu6DpQV7R3Kij4aZcXAgrJiMkRZMYKjrHjXgbJnm6EsUM5Co+zfbCgLlOPQKM+GGMoC5Qg0yrFAQ1mgPAeNcibcUBYoe6FRzicxlAXK59AoV6UylAXKR9Ao19ZmKAuU96FR7qjQUBYo30Kj3FenoSxQ3qBR7q7WUNZ8WfIHzN7PzlyBKZMAAAAASUVORK5CYII=');
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
  background: #fffffff;
}
/* Tab Bar */
#bar a{
    margin: 0px;
    padding-top:5px;
    padding-left: 20px;
    padding-right: 20px;
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

'''

HTML_HEADER = \
'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<link rel="icon" type"image/png" href="data:image/png;base64,%(icon)s"/>
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

<div class="main">
'''

TABS_END = \
'''
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
    document.getElementById(other_id).className = "tab_hidden";
    document.getElementById(load_id).className = "";
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
<h1 id="title"><img src="data:image/bmp;base64,%(icon)s"/>Rummage Results</h1>
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
    html.write('<div id="tab1">')
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


def export(export_html, result_list, result_content_list):

    with codecs.open(export_html, "w", encoding="utf-8") as html:
        html.write(
            HTML_HEADER % {
                "js": SORT_JS,
                "morejs": LOAD_TAB,
                "css": CSS_HTML,
                "icon": base64.b64encode(glass.GetData())
            }
        )
        html.write(BODY_START % {"icon": base64.b64encode(rum_64.GetData())})
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
