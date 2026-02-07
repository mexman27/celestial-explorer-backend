import logging

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

from apps.gaia.clients.exoplanet_archive import ExoplanetArchiveClient
from apps.gaia.models import Planet, Star
from apps.gaia.utils import ra_dec_to_cartesian


class Command(BaseCommand):
    help = "Ingest exoplanets from NASA Exoplanet Archive into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, default=5000,
            help="Maximum number of planets to fetch (default: 5000)",
        )
        parser.add_argument(
            "--max-distance", type=float, default=50,
            help="Maximum distance in parsecs (default: 50)",
        )
        parser.add_argument(
            "--clear", action="store_true",
            help="Clear existing planet data before ingesting",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Fetch and log data without writing to DB",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        max_distance = options["max_distance"]
        clear = options["clear"]
        dry_run = options["dry_run"]

        logger.info("Fetching up to %d planets within %s pc", limit, max_distance)
        self.stdout.write(f"Fetching up to {limit} planets within {max_distance} pc...")

        client = ExoplanetArchiveClient()
        rows = client.query_confirmed_planets(
            max_distance_pc=max_distance, limit=limit,
        )
        logger.info("Received %d rows from NASA Exoplanet Archive", len(rows))
        self.stdout.write(f"Received {len(rows)} rows from NASA Exoplanet Archive")

        if dry_run:
            for row in rows[:5]:
                self.stdout.write(f"  {row}")
            self.stdout.write("Dry run — no data written.")
            return

        if clear:
            deleted, _ = Planet.objects.all().delete()
            self.stdout.write(f"Cleared {deleted} existing planets")

        created = 0
        updated = 0
        for row in rows:
            pl_name = row.get("pl_name", "").strip()
            if not pl_name:
                continue

            distance = row.get("sy_dist")
            ra = row.get("ra")
            dec = row.get("dec")
            x, y, z = ra_dec_to_cartesian(ra, dec, distance)

            host_star = None
            hostname = row.get("hostname", "").strip()
            if hostname:
                host_star = Star.objects.filter(name__icontains=hostname).first()

            planet_type = self._classify_planet(row)

            _, was_created = Planet.objects.update_or_create(
                catalog_id=f"NEA-{pl_name}",
                defaults={
                    "name": pl_name,
                    "right_ascension": ra or 0,
                    "declination": dec or 0,
                    "distance_parsecs": distance,
                    "planet_type": planet_type,
                    "is_exoplanet": True,
                    "host_star_name": hostname,
                    "host_star": host_star,
                    "mass_earth": row.get("pl_bmasse"),
                    "mass_jupiter": row.get("pl_bmassj"),
                    "radius_earth": row.get("pl_rade"),
                    "radius_jupiter": row.get("pl_radj"),
                    "density": row.get("pl_dens"),
                    "surface_temperature_kelvin": (
                        int(row["pl_eqt"])
                        if row.get("pl_eqt") is not None
                        else None
                    ),
                    "orbital_period_days": row.get("pl_orbper"),
                    "semi_major_axis_au": row.get("pl_orbsmax"),
                    "eccentricity": row.get("pl_orbeccen"),
                    "inclination_deg": row.get("pl_orbincl"),
                    "discovery_year": row.get("disc_year"),
                    "detection_method": self._map_detection(
                        row.get("discoverymethod", "")
                    ),
                    "x_parsecs": x,
                    "y_parsecs": y,
                    "z_parsecs": z,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        logger.info("Planets ingestion done: %d created, %d updated", created, updated)
        self.stdout.write(
            self.style.SUCCESS(
                f"Done: {created} created, {updated} updated"
            )
        )

    def _classify_planet(self, row):
        mass_earth = row.get("pl_bmasse")
        radius_earth = row.get("pl_rade")

        if mass_earth is None and radius_earth is None:
            return "unknown"

        r = radius_earth or 0
        m = mass_earth or 0

        if r < 1.6 or (m > 0 and m < 5):
            return "rocky"
        if r < 4 or (m > 0 and m < 20):
            return "super_earth"
        if m > 50 or r > 6:
            return "gas_giant"
        return "mini_neptune"

    def _map_detection(self, method):
        mapping = {
            "Transit": "transit",
            "Radial Velocity": "radial_velocity",
            "Imaging": "direct_imaging",
            "Microlensing": "microlensing",
            "Transit Timing Variations": "timing",
            "Astrometry": "astrometry",
        }
        return mapping.get(method, "other")
