import math


def ra_dec_to_cartesian(ra_deg, dec_deg, distance_pc):
    """Convert RA/Dec/distance to cartesian (x, y, z) in parsecs."""
    if distance_pc is None:
        return None, None, None
    ra_rad = math.radians(ra_deg)
    dec_rad = math.radians(dec_deg)
    x = distance_pc * math.cos(dec_rad) * math.cos(ra_rad)
    y = distance_pc * math.cos(dec_rad) * math.sin(ra_rad)
    z = distance_pc * math.sin(dec_rad)
    return x, y, z
