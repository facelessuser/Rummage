"""Safely import other modules without overriding with locals."""
import sys
# Prevent us from loading local packages with `python -m`
# Comment this out if you want rummage to load a local package
# for testing.

if '' in sys.path:
    sys.path.remove('')
