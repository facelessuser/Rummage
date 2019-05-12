"""Patch graphical user interface file."""
import codecs
import re

filename = 'rummage/lib/gui/gui.py'

with codecs.open(filename, 'r', encoding='utf-8') as f:
    text = f.read()

# Add collapsible pane replacement
text = re.sub(
    r'^((?:import|from)(?! \.controls\.collapsible_pane).*?)(\r?\n){2}',
    r'\1\2from .controls.collapsible_pane import CollapsiblePane\2\2GUI_PATCHED = True\2\2',
    text,
    flags=re.M
)

# Replace old collapsible pane
text = re.sub(
    r'\bwx\.(?=CollapsiblePane\b)',
    '',
    text
)

with codecs.open(filename, 'w', encoding='utf-8') as f:
    f.write(text)
