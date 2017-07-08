"""Script to patch wxFormBuilder output of wxPython files for version 4.0."""
from __future__ import print_function
import re
import os
import codecs

RE_ADD_WX_ADV = re.compile(r'(import wx)\n')
RE_SIZE_HINTS_SZ = re.compile(r'\bSetSizeHintsSz\b')
RE_ADD_SPACER = re.compile(r'\bAddSpacer\b')
RE_APPEND_ITEM = re.compile(r'\bAppendItem\b')
RE_ADV = re.compile(r'\b(wx\.)(GenericDatePickerCtrl|DP_)')
RE_ST = re.compile(r'\b(wx\.ST)(_)')

gui = os.path.join('rummage', 'lib', 'gui', 'gui.py')

with codecs.open(gui, 'r', encoding="utf-8") as f:
    buf = f.read().replace('\r', '')

    buf = RE_ADD_WX_ADV.sub(r'\1\nimport wx.adv\n', buf)
    buf = RE_SIZE_HINTS_SZ.sub('SetSizeHints', buf)
    buf = RE_ADD_SPACER.sub('Add', buf)
    buf = RE_APPEND_ITEM.sub('Append', buf)
    buf = RE_ADV.sub(r'\1adv.\2', buf)
    buf = RE_ST.sub(r'\1B\2', buf)

with codecs.open(gui, 'w', encoding='utf-8') as f:
    f.write(buf.strip() + '\n')
