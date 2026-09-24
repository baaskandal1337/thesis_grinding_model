from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class Stream:
    solid_tph: float
    water_m3h: float
    psd: np.ndarray  # mass fractions by size class (sum=1)


def normalize_psd(psd: np.ndarray) -> np.ndarray:
    psd = np.asarray(psd, dtype=float)
    s = float(psd.sum())
    if s <= 0:
        raise ValueError("PSD sum must be > 0")
    return psd / s


def mix(streams: list[Stream]) -> Stream:
    solid = float(sum(s.solid_tph for s in streams))
    water = float(sum(s.water_m3h for s in streams))

    if solid <= 0:
        # fallback: take PSD from first stream
        psd = streams[0].psd.copy()
    else:
        psd = sum(s.solid_tph * s.psd for s in streams) / solid

    return Stream(solid, water, normalize_psd(psd))