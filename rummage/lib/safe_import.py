"""Safely import other modules without overriding with locals."""
import sys
# Prevent us from loading local packages
# Comment this out if you want rummage to load a local package
# for testing.
sys.path.remove('')
