"""Normalize Mode S ICAO hex and callsigns for feeder/stream/API consistency."""


def normalize_mode_s_hex(value: str) -> str:
    """Uppercase 6-digit ICAO24; strip noise; zero-pad if short."""
    if not value:
        return ''
    h = ''.join(c for c in value.strip().upper() if c in '0123456789ABCDEF')
    if not h:
        return ''
    if len(h) < 6:
        h = h.zfill(6)
    elif len(h) > 6:
        h = h[-6:]
    return h


def normalize_callsign(value: str) -> str:
    """Strip, uppercase, remove whitespace (ADS-B ids are space-padded; APIs expect e.g. UAL123)."""
    if not value:
        return ''
    return ''.join(value.strip().upper().split())
