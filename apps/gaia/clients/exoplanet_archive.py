import logging
import re

import requests

logger = logging.getLogger(__name__)

NASA_TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"


def _clean_adql(adql):
    """Collapse whitespace in ADQL to a single-line query."""
    return re.sub(r"\s+", " ", adql).strip()


class ExoplanetArchiveClient:
    """Client for the NASA Exoplanet Archive TAP service."""

    def __init__(self, timeout=120):
        self.timeout = timeout

    def query(self, adql, max_rec=500):
        """
        Execute an ADQL query against the NASA Exoplanet Archive.

        Returns a list of row dicts.
        """
        cleaned = _clean_adql(adql)
        logger.debug("NASA ADQL query: %s", cleaned)
        response = requests.post(
            NASA_TAP_URL,
            data={
                "REQUEST": "doQuery",
                "LANG": "ADQL",
                "FORMAT": "json",
                "QUERY": cleaned,
                "MAXREC": str(max_rec),
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        rows = response.json()
        logger.info("NASA query returned %d rows", len(rows))
        return rows

    def query_confirmed_planets(self, max_distance_pc=50, limit=5000):
        """Fetch confirmed exoplanets within a given distance."""
        logger.info("Fetching planets within %s pc (limit=%d)", max_distance_pc, limit)
        adql = f"""
            SELECT TOP {limit}
                pl_name, hostname, discoverymethod,
                disc_year, pl_orbper, pl_orbsmax,
                pl_orbeccen, pl_orbincl,
                pl_bmasse, pl_bmassj,
                pl_rade, pl_radj,
                pl_dens, pl_eqt,
                ra, dec, sy_dist
            FROM ps
            WHERE default_flag = 1
                AND sy_dist IS NOT NULL
                AND sy_dist < {max_distance_pc}
            ORDER BY sy_dist ASC
        """
        return self.query(adql, max_rec=limit)
