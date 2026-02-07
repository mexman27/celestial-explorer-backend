import re

import requests

GAIA_TAP_URL = "https://gea.esac.esa.int/tap-server/tap/sync"
PAGE_SIZE = 2000


def _clean_adql(adql):
    """Collapse whitespace in ADQL to a single-line query."""
    return re.sub(r"\s+", " ", adql).strip()


class GaiaTapClient:
    """Client for the ESA Gaia TAP (Table Access Protocol) service."""

    def __init__(self, timeout=120):
        self.timeout = timeout

    def query(self, adql, max_rec=2000):
        """
        Execute an ADQL query against Gaia DR3.

        Returns a list of row dicts.
        """
        response = requests.post(
            GAIA_TAP_URL,
            data={
                "REQUEST": "doQuery",
                "LANG": "ADQL",
                "FORMAT": "json",
                "QUERY": _clean_adql(adql),
                "MAXREC": str(max_rec),
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return self._parse_response(data)

    def query_nearby_stars(self, max_distance_pc=50, limit=None):
        """
        Fetch stars within a given distance from Gaia DR3.
        Paginates automatically using OFFSET if limit is None or > PAGE_SIZE.
        """
        all_rows = []
        offset = 0
        batch_size = PAGE_SIZE

        while True:
            remaining = (limit - len(all_rows)) if limit else batch_size
            fetch_count = min(batch_size, remaining)

            adql = f"""
                SELECT TOP {fetch_count}
                    source_id, designation,
                    ra, dec, parallax,
                    phot_g_mean_mag, bp_rp, teff_gspphot,
                    pmra, pmdec, radial_velocity,
                    distance_gspphot
                FROM gaiadr3.gaia_source
                WHERE distance_gspphot IS NOT NULL
                    AND distance_gspphot < {max_distance_pc}
                    AND phot_g_mean_mag IS NOT NULL
                ORDER BY phot_g_mean_mag ASC
                OFFSET {offset}
            """
            rows = self.query(adql, max_rec=fetch_count)
            all_rows.extend(rows)

            if len(rows) < fetch_count:
                break
            if limit and len(all_rows) >= limit:
                break

            offset += fetch_count

        return all_rows

    def _parse_response(self, data):
        """Convert Gaia TAP JSON response to a list of dicts."""
        if "data" not in data or "metadata" not in data:
            return []
        columns = [col["name"] for col in data["metadata"]]
        return [dict(zip(columns, row)) for row in data["data"]]
