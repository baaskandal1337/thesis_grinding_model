import numpy as np
from ..streams import Stream, normalize_psd


class CyclonePartition:
    """
    Partition curve: probability of reporting to overflow by size class.
    sizes_mm: representative size per class (e.g., geometric mean of bounds).
    """

    def __init__(self, d50_mm: float, sharpness: float, bypass: float, sizes_mm: np.ndarray):
        self.d50 = float(d50_mm)
        self.sharp = float(sharpness)
        self.bypass = float(bypass)
        self.sizes = np.asarray(sizes_mm, dtype=float)

    def _P_overflow(self) -> np.ndarray:
        d = self.sizes
        x = (d / self.d50) ** self.sharp
        P = self.bypass + (1.0 - self.bypass) * (1.0 / (1.0 + x))
        return np.clip(P, 0.0, 1.0)

    def split(self, feed: Stream) -> tuple[Stream, Stream]:
        P = self._P_overflow()
        p = feed.psd

        of_solid = feed.solid_tph * float((P * p).sum())
        uf_solid = feed.solid_tph - of_solid

        of_psd = normalize_psd(P * p)
        uf_psd = normalize_psd((1.0 - P) * p)

        # Water split simplification: all water to overflow
        of = Stream(of_solid, feed.water_m3h, of_psd)
        uf = Stream(uf_solid, 0.0, uf_psd)
        return of, uf