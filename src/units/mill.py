import numpy as np
from ..streams import Stream, normalize_psd


class SimpleGrindingMill:
    """
    Simplified steady-state grinding:
    a fraction 'intensity' of each size class moves to the next finer class.
    intensity in [0..1].
    """

    def __init__(self, intensity: float):
        self.intensity = float(intensity)

    def apply(self, feed: Stream) -> Stream:
        p = feed.psd.copy()
        n = len(p)
        out = p.copy()

        k = self.intensity
        for i in range(n - 1):
            moved = k * p[i]
            out[i] -= moved
            out[i + 1] += moved

        return Stream(feed.solid_tph, feed.water_m3h, normalize_psd(out))