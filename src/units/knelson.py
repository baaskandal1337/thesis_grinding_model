from ..streams import Stream


class Knelson:
    def __init__(self, concentrate_solid_tph: float, fluid_water_m3h: float):
        self.conc_solid = float(concentrate_solid_tph)
        self.fluid = float(fluid_water_m3h)

    def split(self, feed: Stream) -> tuple[Stream, Stream]:
        conc_s = min(self.conc_solid, feed.solid_tph)
        tail_s = feed.solid_tph - conc_s

        conc = Stream(conc_s, 0.0, feed.psd.copy())
        tail = Stream(tail_s, feed.water_m3h + self.fluid, feed.psd.copy())
        return tail, conc