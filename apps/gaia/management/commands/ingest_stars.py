from django.core.management.base import BaseCommand

from apps.gaia.clients.gaia_tap import GaiaTapClient
from apps.gaia.models import Star
from apps.gaia.utils import ra_dec_to_cartesian


class Command(BaseCommand):
    help = "Ingest stars from ESA Gaia DR3 into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, default=None,
            help="Maximum number of stars to fetch (default: all)",
        )
        parser.add_argument(
            "--max-distance", type=float, default=50,
            help="Maximum distance in parsecs (default: 50)",
        )
        parser.add_argument(
            "--clear", action="store_true",
            help="Clear existing star data before ingesting",
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

        label = f"up to {limit}" if limit else "all"
        self.stdout.write(f"Fetching {label} stars within {max_distance} pc...")

        client = GaiaTapClient()
        rows = client.query_nearby_stars(
            max_distance_pc=max_distance, limit=limit,
        )
        self.stdout.write(f"Received {len(rows)} rows from Gaia TAP")

        if dry_run:
            for row in rows[:5]:
                self.stdout.write(f"  {row}")
            self.stdout.write("Dry run — no data written.")
            return

        if clear:
            deleted, _ = Star.objects.all().delete()
            self.stdout.write(f"Cleared {deleted} existing stars")

        created = 0
        updated = 0
        for row in rows:
            source_id = str(row.get("source_id", ""))
            if not source_id:
                continue

            distance = row.get("distance_gspphot")
            ra = row.get("ra")
            dec = row.get("dec")
            x, y, z = ra_dec_to_cartesian(ra, dec, distance)

            _, was_created = Star.objects.update_or_create(
                gaia_source_id=source_id,
                defaults={
                    "name": row.get("designation", f"Gaia DR3 {source_id}"),
                    "catalog_id": f"GDR3-{source_id}",
                    "right_ascension": ra or 0,
                    "declination": dec or 0,
                    "distance_parsecs": distance,
                    "apparent_magnitude": row.get("phot_g_mean_mag"),
                    "temperature_kelvin": (
                        int(row["teff_gspphot"])
                        if row.get("teff_gspphot") is not None
                        else None
                    ),
                    "proper_motion_ra": row.get("pmra"),
                    "proper_motion_dec": row.get("pmdec"),
                    "radial_velocity": row.get("radial_velocity"),
                    "x_parsecs": x,
                    "y_parsecs": y,
                    "z_parsecs": z,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: {created} created, {updated} updated"
            )
        )
