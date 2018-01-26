"""Export HTML."""
from __future__ import unicode_literals
import webbrowser
import re
import time
import os
import codecs
import base64
import json
import subprocess
from .. import data
from ..localization import _, get_current_domain
from ... import util
from ... import rumcore


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
        )
    )


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
<td>%(matches)s</td>
<td>%(extensions)s</td>
<td sorttable_customkey="%(size_sort)s">%(size)s</td>
<td>%(path)s</td>
<td>%(encoding)s</td>
<td sorttable_customkey="%(mod_sort)s">%(modified)s</td>
<td sorttable_customkey="%(cre_sort)s">%(created)s</td>
</tr>
'''

RESULT_TABLE_HEADER = '''
<tr>
<th>%(file)s</th>
<th>%(matches)s</th>
<th>%(extensions)s</th>
<th>%(size)s</th>
<th>%(path)s</th>
<th>%(encoding)s</th>
<th>%(modified)s</th>
<th>%(created)s</th>
</tr>
'''

RESULT_CONTENT_ROW = '''
<tr>
<td sorttable_customkey="%(file_sort)s">%(file)s</td>
<td>%(line)s</td>
<td>%(matches)s</td>
<td>%(extensions)s</td>
<td>%(context)s</td>
</tr>
'''

RESULT_CONTENT_TABLE_HEADER = '''
<tr>
<th>%(file)s</th>
<th>%(line)s</th>
<th>%(matches)s</th>
<th>%(extensions)s</th>
<th>%(context)s</th>
</tr>
'''

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

TABS_END = '''
<div id="search_div"><label id="search_label">%(label)s %(search)s</label></div>
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
<h1 id="title"><img src="data:image/bmp;base64,%(icon)s"/>%(title)s</h1>
'''

BODY_END = '''
</body>
</html>
'''


def export_result_list(res, html):
    """Export result list."""

    if len(res) == 0:
        return
    html.write('<div id="tab1">')
    html.write('<table class="sortable">')
    html.write(
        RESULT_TABLE_HEADER % {
            "file": html_encode(_("File")),
            "matches": html_encode(_("Matches")),
            "extensions": html_encode(_("Extensions")),
            "size": html_encode(_("Size")),
            "path": html_encode(_("Path")),
            "encoding": html_encode(_("Encoding")),
            "modified": html_encode(_("Modified")),
            "created": html_encode(_("Created"))
        }
    )

    for item in res.values():
        html.write(
            RESULT_ROW % {
                "file": html_encode(item[0]),
                "matches": util.to_ustr(item[1]),
                "extensions": html_encode(item[2]),
                "size_sort": util.to_ustr(item[3]),
                "size": '%.2fKB' % item[3],
                "path": html_encode(item[4]),
                "encoding": item[5],
                "mod_sort": util.to_ustr(item[6]),
                "modified": time.ctime(item[6]),
                "cre_sort": util.to_ustr(item[7]),
                "created": time.ctime(item[7])
            }
        )
    html.write('</table>')
    html.write('</div>')


def export_result_content_list(res, html):
    """Export result content list."""

    if len(res) == 0:
        return
    html.write('<div id="tab2"">')
    html.write('<table class="sortable">')
    html.write(
        RESULT_CONTENT_TABLE_HEADER % {
            "file": html_encode(_("File")),
            "line": html_encode(_("Line")),
            "matches": html_encode(_("Matches")),
            "extensions": html_encode(_("Extensions")),
            "context": html_encode(_("Context"))
        }
    )

    for item in res.values():
        html.write(
            RESULT_CONTENT_ROW % {
                "file_sort": html_encode(os.path.join(item[0][1], item[0][0])),
                "file": html_encode(item[0][0]),
                "line": util.to_ustr(item[1]),
                "matches": util.to_ustr(item[2]),
                "extensions": html_encode(item[3]),
                "context": html_encode(item[4])
            }
        )
    html.write('</table>')
    html.write('</div>')


def open_in_browser(name):
    """Auto open HTML."""

    platform = util.platform()
    if platform == "osx":
        web_handler = None
        try:
            launch_services = os.path.expanduser(
                '~/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure.plist'
            )
            if not os.path.exists(launch_services):
                launch_services = os.path.expanduser('~/Library/Preferences/com.apple.LaunchServices.plist')
            with open(launch_services, "rb") as f:
                content = f.read()
            args = ["plutil", "-convert", "json", "-o", "-", "--", "-"]
            p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            p.stdin.write(content)
            out = p.communicate()[0]
            plist = json.loads(util.to_ustr(out))
            for handler in plist['LSHandlers']:
                if handler.get('LSHandlerURLScheme', '') == "http":
                    web_handler = handler.get('LSHandlerRoleAll', None)
                    break
        except Exception:
            pass
        if web_handler is not None:
            subprocess.Popen(['open', '-b', web_handler, name])
        else:
            subprocess.Popen(['open', name])
    elif platform == "windows":
        webbrowser.open(name, new=2)
    else:
        try:
            # Maybe...?
            subprocess.Popen(['xdg-open', name])
        except OSError:
            webbrowser.open(name, new=2)
            # Well we gave it our best...


def export(export_html, chain, result_list, result_content_list):
    """Export the results as HTML."""

    title = html_encode(_("Rummage Results"))

    with codecs.open(export_html, "w", encoding="utf-8") as html:
        html.write(
            HTML_HEADER % {
                "js": data.get_file('sorttable.js'),
                "morejs": LOAD_TAB,
                "css": data.get_file('results.css'),
                "icon": util.to_ustr(base64.b64encode(data.get_image('glass.png').GetData())),
                "title": title,
                "lang": get_current_domain()
            }
        )
        html.write(
            BODY_START % {
                "title": title,
                "icon": util.to_ustr(base64.b64encode(data.get_image('rummage.png').GetData()))
            }
        )

        html.write(
            (TABS_START if len(result_content_list) else TABS_START_SINGLE) % {
                "file_tab": html_encode(_("Files")),
                "content_tab": html_encode(_("Content"))
            }
        )
        export_result_list(result_list, html)
        export_result_content_list(result_content_list, html)

        search_label_regex = html_encode(_("Regex search:"))
        search_label_literal = html_encode(_("Literal search:"))
        for pattern, replace, flags in chain:
            html.write(
                TABS_END % {
                    "search": html_encode(pattern),
                    "label": search_label_literal if flags & rumcore.LITERAL else search_label_regex
                }
            )
        html.write('</div>')
        html.write(TAB_INIT)
        html.write(BODY_END)

    open_in_browser(html.name)
