from coloraide import Color as Base
from coloraide import algebra as alg


def reverse_channels(color, alpha=False):
    """Reverse the color channels."""

    if alpha:
        return (
            ((color & 0xFF000000) >> 24) | ((color & 0xFF0000) >> 8) | ((color & 0xFF00) << 8) | ((color & 0xFF) << 24)
        )
    else:
        return ((color & 0xFF0000) >> 16) | (color & 0xFF00) | ((color & 0xFF) << 16)


class Color(Base):
    """Color object."""

    def to_wxbgr(self):
        """Get the the wxPython RGB value."""

        r, g, b = [alg.clamp(int(alg.round_half_up(c * 255)), 0, 255) for c in self.convert('srgb').coords(nans=False)]
        a = alg.clamp(int(alg.round_half_up(self.alpha(nans=False))))
        color = (r << 24) | (g << 16) | (b << 8) | a
        return reverse_channels(color, alpha=True)

    @classmethod
    def from_wxbgr(cls, color):
        """Get a color object from the wxPython RGB value."""

        color = reverse_channels(color, alpha=True)

        if color > 0xFFFFFFFF or color < 0:
            raise ValueError("Color value out of range")

        rgb = (
            alg.clamp((color & 0xFF000000) >> 24, 0, 255) / 255,
            alg.clamp((color & 0xFF0000) >> 16, 0, 255) / 255,
            alg.clamp((color & 0xFF00) >> 8, 0, 255) / 255
        )
        a = alg.clamp((color & 0xFF), 0, 255) / 255
        return cls('srgb', rgb, a)

    @classmethod
    def from_rgb(cls, color):
        """Get color from RGB values between (0 - 255)."""

        if len(color) == 3:
            return cls('srgb', [c / 255 for c in color])
        else:
            return cls('srgb', [c / 255 for c in color[:-1]], color[-1] / 255)

    def to_rgb(self, alpha=False):
        """Get RGB values between 0 - 255."""

        values = [alg.clamp(int(alg.round_half_up(c * 255)), 0, 255) for c in self.coords(nans=False)]
        if alpha:
            values.append(alg.clamp(int(alg.round_half_up(self.alpha(nans=False) * 255)), 0, 255))
        return values
