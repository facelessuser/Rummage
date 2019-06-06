"""Utilities."""
import os


def which(executable):
    """See if executable exists."""

    location = None
    if os.path.basename(executable) != executable:
        if os.path.isfile(executable):
            location = executable
    else:
        paths = [x for x in os.environ["PATH"].split(os.pathsep) if not x.isspace()]
        for path in paths:
            exe = os.path.join(path, executable)
            if os.path.isfile(exe):
                location = exe
                break
    return location
