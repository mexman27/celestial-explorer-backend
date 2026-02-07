import requests

GAIA_TAP_URL = "https://gea.esac.esa.int/tap-server/tap/sync"


class GaiaTapClient:
    """Client for the ESA Gaia TAP (Table Access Protocol) service."""

    def __init__(self, timeout=60):
        self.timeout = timeout

    def query(self, adql, max_rec=500):
        """
        Execute an ADQL query against Gaia DR3.

        Returns a list of row dicts.
        """
        response = requests.get(
            GAIA_TAP_URL,
            params={
                "REQUEST": "doQuery",
                "LANG": "ADQL",
                "FORMAT": "json",
                "QUERY": adql,
                "MAXREC": str(max_rec),
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return self._parse_response(data)

    def query_nearby_stars(self, max_distance_pc=500, limit=500):
        """Fetch bright stars within a given distance from Gaia DR3."""
        adql = f"""
            SELECT TOP {limit}
                source_id, designation,
                ra, dec, parallax,
                phot_g_mean_mag, bp_rp,
                teff_gspphot, radius_gspphot, lum_gspphot,
                pmra, pmdec, radial_velocity,
                distance_gspphot
            FROM gaiadr3.gaia_source
            WHERE distance_gspphot IS NOT NULL
                AND distance_gspphot < {max_distance_pc}
                AND phot_g_mean_mag IS NOT NULL
            ORDER BY phot_g_mean_mag ASC
        """
        return self.query(adql, max_rec=limit)

    def _parse_response(self, data):
        """Convert Gaia TAP JSON response to a list of dicts."""
        if "data" not in data or "metadata" not in data:
            return []
        columns = [col["name"] for col in data["metadata"]]
        return [dict(zip(columns, row)) for row in data["data"]]
