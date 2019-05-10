"""
Image tinting.

Licensed under MIT
Copyright (c) 2015 - 2016 Isaac Muse <isaacmuse@gmail.com>
"""
from .png import Reader, Writer
import io


def tint_png(byte_string, color):
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
            rgba.apply_alpha(*row[start:start + 3])
            p[y] += [rgba.r, rgba.g, rgba.b, row[start + 3]]
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
