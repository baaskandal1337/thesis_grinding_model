import numpy as np
from ..streams import Stream, normalize_psd


class ProtectiveScreen2mm:
    """
    Since the PSD grid has no +2 mm class, we model the screen by sending a
    small share of the top class (2-1 mm) to oversize (to ball mill).
    All added spray water is assumed to go to undersize (simplification).
    """

    def __init__(self, oversize_share_of_top_class: float, spray_water_m3h: float):
        self.r = float(oversize_share_of_top_class)  # 0..1
        self.spray = float(spray_water_m3h)

    def split(self, feed: Stream) -> tuple[Stream, Stream]:
        feed2 = Stream(feed.solid_tph, feed.water_m3h + self.spray, feed.psd)

        p = feed2.psd
        top = 0  # index of class 2-1 mm

        os_solid = feed2.solid_tph * (self.r * p[top])
        us_solid = feed2.solid_tph - os_solid

        os_psd = np.zeros_like(p)
        if os_solid > 0:
            os_psd[top] = 1.0
        else:
            os_psd = p.copy()

        us_psd = p.copy()
        us_psd[top] = max(0.0, us_psd[top] - self.r * p[top])
        us_psd = normalize_psd(us_psd)

        os = Stream(os_solid, 0.0, os_psd)
        us = Stream(us_solid, feed2.water_m3h, us_psd)
        return us, os