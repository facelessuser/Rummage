"""Color management."""
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

    def to_wxbgr(self, alpha=True):
        """Get the wxPython RGB value."""

        r, g, b = [alg.clamp(int(alg.round_half_up(c * 255)), 0, 255) for c in self.convert('srgb').coords(nans=False)]
        a = alg.clamp(int(alg.round_half_up(self.alpha(nans=False)))) if alpha else 0xFF
        color = (r << 24) | (g << 16) | (b << 8) | a
        return reverse_channels(color, alpha=True)

    @classmethod
    def from_wxbgr(cls, color, alpha=True):
        """Get a color object from the wxPython RGB value."""

        color = reverse_channels(color, alpha=True)

        if color > 0xFFFFFFFF or color < 0:
            raise ValueError("Color value out of range")

        rgb = (
            alg.clamp((color & 0xFF000000) >> 24, 0, 255) / 255,
            alg.clamp((color & 0xFF0000) >> 16, 0, 255) / 255,
            alg.clamp((color & 0xFF00) >> 8, 0, 255) / 255
        )
        a = (alg.clamp((color & 0xFF), 0, 255) / 255) if alpha else 1
        return cls('srgb', rgb, a)
