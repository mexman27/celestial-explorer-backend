import logging

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

from apps.gaia.models import Galaxy
from apps.gaia.utils import ra_dec_to_cartesian


# Local Group + notable nearby galaxies bundled as seed data
LOCAL_GROUP_GALAXIES = [
    {
        "name": "Milky Way",
        "catalog_id": "LG-MW",
        "morphology": "barred_spiral",
        "hubble_type": "SBbc",
        "ra": 266.405, "dec": -28.936,
        "distance_pc": 0.008,
        "apparent_magnitude": None,
        "absolute_magnitude": -20.9,
        "diameter_kpc": 26.8,
        "mass_solar": 1.5e12,
        "num_stars_estimate": 200_000_000_000,
        "galaxy_group": "Local Group",
    },
    {
        "name": "Andromeda Galaxy",
        "catalog_id": "M31",
        "morphology": "spiral",
        "hubble_type": "SA(s)b",
        "ra": 10.6847, "dec": 41.2687,
        "distance_pc": 778_000,
        "apparent_magnitude": 3.44,
        "absolute_magnitude": -21.5,
        "diameter_kpc": 46.56,
        "mass_solar": 1.5e12,
        "num_stars_estimate": 1_000_000_000_000,
        "galaxy_group": "Local Group",
        "messier_number": "M31",
        "ngc_number": "NGC 224",
    },
    {
        "name": "Triangulum Galaxy",
        "catalog_id": "M33",
        "morphology": "spiral",
        "hubble_type": "SA(s)cd",
        "ra": 23.4621, "dec": 30.6602,
        "distance_pc": 847_000,
        "apparent_magnitude": 5.72,
        "absolute_magnitude": -18.87,
        "diameter_kpc": 18.74,
        "mass_solar": 5.0e10,
        "num_stars_estimate": 40_000_000_000,
        "galaxy_group": "Local Group",
        "messier_number": "M33",
        "ngc_number": "NGC 598",
    },
    {
        "name": "Large Magellanic Cloud",
        "catalog_id": "LMC",
        "morphology": "irregular",
        "hubble_type": "SB(s)m",
        "ra": 80.8942, "dec": -69.7561,
        "distance_pc": 49_970,
        "apparent_magnitude": 0.9,
        "absolute_magnitude": -18.5,
        "diameter_kpc": 4.3,
        "mass_solar": 1.0e10,
        "num_stars_estimate": 30_000_000_000,
        "galaxy_group": "Local Group",
    },
    {
        "name": "Small Magellanic Cloud",
        "catalog_id": "SMC",
        "morphology": "dwarf_irregular",
        "hubble_type": "SB(s)m pec",
        "ra": 13.1867, "dec": -72.8286,
        "distance_pc": 61_000,
        "apparent_magnitude": 2.7,
        "absolute_magnitude": -17.1,
        "diameter_kpc": 2.14,
        "mass_solar": 6.5e9,
        "num_stars_estimate": 3_000_000_000,
        "galaxy_group": "Local Group",
    },
    {
        "name": "Sagittarius Dwarf Elliptical Galaxy",
        "catalog_id": "SagDEG",
        "morphology": "dwarf_elliptical",
        "hubble_type": "dSph/E7",
        "ra": 283.8313, "dec": -30.5453,
        "distance_pc": 24_000,
        "apparent_magnitude": 4.5,
        "absolute_magnitude": -13.5,
        "diameter_kpc": 3.0,
        "mass_solar": 4.0e8,
        "galaxy_group": "Local Group",
    },
    {
        "name": "Canis Major Dwarf Galaxy",
        "catalog_id": "CMa-Dwarf",
        "morphology": "dwarf_irregular",
        "hubble_type": "dIrr",
        "ra": 108.15, "dec": -27.67,
        "distance_pc": 7_660,
        "apparent_magnitude": None,
        "absolute_magnitude": -14.5,
        "diameter_kpc": 1.0,
        "mass_solar": 1.0e8,
        "galaxy_group": "Local Group",
    },
    {
        "name": "Ursa Minor Dwarf",
        "catalog_id": "UMi-Dwarf",
        "morphology": "dwarf_spheroidal",
        "hubble_type": "dSph",
        "ra": 227.2854, "dec": 67.2225,
        "distance_pc": 76_000,
        "apparent_magnitude": 11.9,
        "absolute_magnitude": -8.8,
        "diameter_kpc": 0.64,
        "mass_solar": 2.0e7,
        "galaxy_group": "Local Group",
    },
    {
        "name": "Draco Dwarf",
        "catalog_id": "Draco-Dwarf",
        "morphology": "dwarf_spheroidal",
        "hubble_type": "dSph",
        "ra": 260.0517, "dec": 57.9153,
        "distance_pc": 80_000,
        "apparent_magnitude": 10.9,
        "absolute_magnitude": -8.8,
        "diameter_kpc": 0.72,
        "mass_solar": 2.0e7,
        "galaxy_group": "Local Group",
    },
    {
        "name": "NGC 6822 (Barnard's Galaxy)",
        "catalog_id": "NGC6822",
        "morphology": "irregular",
        "hubble_type": "IB(s)m",
        "ra": 296.2354, "dec": -14.7892,
        "distance_pc": 500_000,
        "apparent_magnitude": 8.1,
        "absolute_magnitude": -15.2,
        "diameter_kpc": 2.3,
        "mass_solar": 1.0e9,
        "galaxy_group": "Local Group",
        "ngc_number": "NGC 6822",
    },
]


class Command(BaseCommand):
    help = "Ingest galaxies from bundled Local Group data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear", action="store_true",
            help="Clear existing galaxy data before ingesting",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Log data without writing to DB",
        )

    def handle(self, *args, **options):
        clear = options["clear"]
        dry_run = options["dry_run"]

        galaxies = LOCAL_GROUP_GALAXIES
        logger.info("Ingesting %d galaxies", len(galaxies))
        self.stdout.write(f"Ingesting {len(galaxies)} galaxies...")

        if dry_run:
            for g in galaxies:
                self.stdout.write(f"  {g['name']} ({g['morphology']})")
            self.stdout.write("Dry run — no data written.")
            return

        if clear:
            deleted, _ = Galaxy.objects.all().delete()
            self.stdout.write(f"Cleared {deleted} existing galaxies")

        created = 0
        updated = 0
        for g in galaxies:
            x, y, z = ra_dec_to_cartesian(
                g["ra"], g["dec"], g.get("distance_pc"),
            )
            _, was_created = Galaxy.objects.update_or_create(
                catalog_id=g["catalog_id"],
                defaults={
                    "name": g["name"],
                    "right_ascension": g["ra"],
                    "declination": g["dec"],
                    "distance_parsecs": g.get("distance_pc"),
                    "morphology": g.get("morphology", "unknown"),
                    "hubble_type": g.get("hubble_type", ""),
                    "apparent_magnitude": g.get("apparent_magnitude"),
                    "absolute_magnitude": g.get("absolute_magnitude"),
                    "diameter_kpc": g.get("diameter_kpc"),
                    "mass_solar": g.get("mass_solar"),
                    "num_stars_estimate": g.get("num_stars_estimate"),
                    "galaxy_group": g.get("galaxy_group", ""),
                    "messier_number": g.get("messier_number", ""),
                    "ngc_number": g.get("ngc_number", ""),
                    "x_parsecs": x,
                    "y_parsecs": y,
                    "z_parsecs": z,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        logger.info("Galaxies ingestion done: %d created, %d updated", created, updated)
        self.stdout.write(
            self.style.SUCCESS(
                f"Done: {created} created, {updated} updated"
            )
        )
