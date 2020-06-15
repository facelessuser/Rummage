"""
Image manipulation.

Licensed under MIT
Copyright (c) 2015 - 2016 Isaac Muse <isaacmuse@gmail.com>
"""
from .png import Reader, Writer
from .rgba import RGBA, round_int, clamp
import io


def tint(byte_string, color, transparency=None):
    """Tint the image and return a byte string."""

    # Read the byte string as a `RGBA` image.
    width, height, pixels, meta = Reader(bytes=byte_string).asRGBA()

    # Tint
    p = []
    y = 0
    for row in pixels:
        p.append([])
        columns = int(len(row) / 4)
        start = 0
        for x in range(columns):
            rgba = color
            rgba.apply_alpha(RGBA(row[start:start + 3]))
            alpha = row[start + 3]
            # Adjust transparency of image if also desired
            if transparency is not None:
                alpha = round_int(clamp(alpha + (255.0 * transparency) - 255.0, 0.0, 255.0))
            p[y] += [rgba.r, rgba.g, rgba.b, alpha]
            start += 4
        y += 1

    # Create bytes buffer for `PNG`
    with io.BytesIO() as f:

        # Write out PNG
        img = Writer(width, height, alpha=True)
        img.write(f, p)

        # Read out PNG bytes and base64 encode
        f.seek(0)

        return f.read()


def transparency(byte_string, transparency):
    """Adjust image transparency."""

    # Read the byte string as a `RGBA` image.
    width, height, pixels, meta = Reader(bytes=byte_string).asRGBA()

    p = []
    y = 0
    for row in pixels:
        p.append([])
        columns = int(len(row) / 4)
        start = 0
        for x in range(columns):
            alpha = row[start + 3]
            alpha = round_int(clamp(alpha + (255.0 * transparency) - 255.0, 0.0, 255.0))
            p[y] += [row[start], row[start + 1], row[start + 2], alpha]
            start += 4
        y += 1

    # Create bytes buffer for `PNG`
    with io.BytesIO() as f:

        # Write out PNG
        img = Writer(width, height, alpha=True)
        img.write(f, p)

        # Read out PNG bytes and base64 encode
        f.seek(0)

        return f.read()
