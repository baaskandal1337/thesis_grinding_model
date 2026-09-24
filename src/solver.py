from __future__ import annotations

from .streams import Stream, mix


def solve_flowsheet(
    fresh_feed: Stream,
    sag_mill,
    bm_mill,
    screen3015,
    knelson,
    cyclone,
    water_to_3012_m3h: float,
    water_to_3017_extra_m3h: float,
    water_to_cyclone_feed_m3h: float,
    bm_feed_dilution_m3h: float,
    bm_discharge_transport_m3h: float,
    relax: float = 0.5,
    max_iter: int = 200,
    tol_rel: float = 1e-4,
):
    # Initial guess for cyclone underflow (solids)
    uf = Stream(0.0, 0.0, fresh_feed.psd.copy())

    for it in range(max_iter):
        uf_old = uf.solid_tph

        # SAG (fresh feed already includes ore moisture + SAG dilution in water)
        sag_prod = sag_mill.apply(fresh_feed)

        # Ball mill preliminary (from UF only)
        bm_feed = Stream(uf.solid_tph, uf.water_m3h + bm_feed_dilution_m3h, uf.psd)
        bm_prod = bm_mill.apply(bm_feed)
        bm_prod = Stream(bm_prod.solid_tph, bm_prod.water_m3h + bm_discharge_transport_m3h, bm_prod.psd)

        # Sump 3012
        sump3012 = mix([sag_prod, bm_prod, Stream(0.0, water_to_3012_m3h, sag_prod.psd)])

        # Protective screen 3015
        us_3015, os_3015 = screen3015.split(sump3012)

        # Recompute ball mill including screen oversize
        bm_feed2 = mix([uf, os_3015])
        bm_feed2 = Stream(bm_feed2.solid_tph, bm_feed2.water_m3h + bm_feed_dilution_m3h, bm_feed2.psd)
        bm_prod2 = bm_mill.apply(bm_feed2)
        bm_prod2 = Stream(bm_prod2.solid_tph, bm_prod2.water_m3h + bm_discharge_transport_m3h, bm_prod2.psd)

        # Recompute sump 3012 and screen
        sump3012 = mix([sag_prod, bm_prod2, Stream(0.0, water_to_3012_m3h, sag_prod.psd)])
        us_3015, os_3015 = screen3015.split(sump3012)

        # Knelson
        tail_kn, conc = knelson.split(us_3015)

        # Sump 3017 (+ extra water if any)
        sump3017 = mix([tail_kn, Stream(0.0, water_to_3017_extra_m3h, tail_kn.psd)])

        # Cyclone feed dilution
        cy_feed = Stream(sump3017.solid_tph, sump3017.water_m3h + water_to_cyclone_feed_m3h, sump3017.psd)

        # Cyclones
        of, uf_calc = cyclone.split(cy_feed)

        # Relax UF solids
        uf = Stream(
            solid_tph=relax * uf_calc.solid_tph + (1.0 - relax) * uf.solid_tph,
            water_m3h=0.0,
            psd=uf_calc.psd,
        )

        # Convergence by UF solids
        if uf_old > 0:
            rel_err = abs(uf.solid_tph - uf_old) / uf_old
        else:
            rel_err = abs(uf.solid_tph - uf_old)

        if rel_err < tol_rel:
            return {
                "iterations": it + 1,
                "sump3012": sump3012,
                "screen_us": us_3015,
                "screen_os": os_3015,
                "kn_tail": tail_kn,
                "kn_conc": conc,
                "sump3017": sump3017,
                "cyclone_of": of,
                "cyclone_uf": uf_calc,
            }

    raise RuntimeError("No convergence")