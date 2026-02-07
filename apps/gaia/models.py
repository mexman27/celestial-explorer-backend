from django.db import models


class CelestialObject(models.Model):
    """Abstract base for all catalog objects."""

    name = models.CharField(max_length=255, db_index=True)
    catalog_id = models.CharField(max_length=100, unique=True, db_index=True)
    right_ascension = models.FloatField(help_text="Right ascension in degrees (0-360)")
    declination = models.FloatField(help_text="Declination in degrees (-90 to +90)")
    distance_parsecs = models.FloatField(null=True, blank=True)
    description = models.TextField(blank=True, default="")

    # Pre-computed cartesian coordinates for Three.js 3D rendering
    x_parsecs = models.FloatField(null=True, blank=True)
    y_parsecs = models.FloatField(null=True, blank=True)
    z_parsecs = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name


class Star(CelestialObject):
    SPECTRAL_CLASSES = [
        ("O", "O — Blue, very hot"),
        ("B", "B — Blue-white"),
        ("A", "A — White"),
        ("F", "F — Yellow-white"),
        ("G", "G — Yellow (Sun-like)"),
        ("K", "K — Orange"),
        ("M", "M — Red dwarf"),
        ("L", "L — Brown dwarf (cool)"),
        ("T", "T — Brown dwarf (methane)"),
        ("Y", "Y — Brown dwarf (ultra-cool)"),
    ]

    apparent_magnitude = models.FloatField(null=True, blank=True)
    absolute_magnitude = models.FloatField(null=True, blank=True)

    spectral_type = models.CharField(
        max_length=20, blank=True, default="",
        help_text="Full spectral classification (e.g., G2V)",
    )
    spectral_class = models.CharField(
        max_length=2, choices=SPECTRAL_CLASSES, blank=True, default="",
    )
    luminosity_solar = models.FloatField(null=True, blank=True)
    mass_solar = models.FloatField(null=True, blank=True)
    radius_solar = models.FloatField(null=True, blank=True)
    temperature_kelvin = models.IntegerField(null=True, blank=True)

    proper_motion_ra = models.FloatField(null=True, blank=True, help_text="mas/yr")
    proper_motion_dec = models.FloatField(null=True, blank=True, help_text="mas/yr")
    radial_velocity = models.FloatField(null=True, blank=True, help_text="km/s")

    hipparcos_id = models.CharField(max_length=20, blank=True, default="", db_index=True)
    gaia_source_id = models.CharField(max_length=30, blank=True, default="", db_index=True)
    henry_draper_id = models.CharField(max_length=20, blank=True, default="")
    bayer_designation = models.CharField(max_length=50, blank=True, default="")
    constellation = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        ordering = ["apparent_magnitude"]
        indexes = [
            models.Index(fields=["spectral_class"]),
            models.Index(fields=["apparent_magnitude"]),
            models.Index(fields=["distance_parsecs"]),
        ]


class Planet(CelestialObject):
    PLANET_TYPES = [
        ("rocky", "Rocky / Terrestrial"),
        ("gas_giant", "Gas Giant"),
        ("ice_giant", "Ice Giant"),
        ("super_earth", "Super-Earth"),
        ("mini_neptune", "Mini-Neptune"),
        ("hot_jupiter", "Hot Jupiter"),
        ("unknown", "Unknown"),
    ]

    DETECTION_METHODS = [
        ("transit", "Transit"),
        ("radial_velocity", "Radial Velocity"),
        ("direct_imaging", "Direct Imaging"),
        ("microlensing", "Microlensing"),
        ("timing", "Transit Timing Variations"),
        ("astrometry", "Astrometry"),
        ("other", "Other"),
    ]

    planet_type = models.CharField(
        max_length=20, choices=PLANET_TYPES, default="unknown",
    )
    is_exoplanet = models.BooleanField(
        default=True,
        help_text="False for Solar System planets, True for exoplanets",
    )

    host_star_name = models.CharField(max_length=255, blank=True, default="")
    host_star = models.ForeignKey(
        Star, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="planets",
    )

    mass_jupiter = models.FloatField(null=True, blank=True)
    mass_earth = models.FloatField(null=True, blank=True)
    radius_jupiter = models.FloatField(null=True, blank=True)
    radius_earth = models.FloatField(null=True, blank=True)
    density = models.FloatField(null=True, blank=True, help_text="g/cm^3")
    surface_temperature_kelvin = models.IntegerField(null=True, blank=True)

    orbital_period_days = models.FloatField(null=True, blank=True)
    semi_major_axis_au = models.FloatField(null=True, blank=True)
    eccentricity = models.FloatField(null=True, blank=True)
    inclination_deg = models.FloatField(null=True, blank=True)

    discovery_year = models.IntegerField(null=True, blank=True)
    detection_method = models.CharField(
        max_length=20, choices=DETECTION_METHODS, blank=True, default="",
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["planet_type"]),
            models.Index(fields=["is_exoplanet"]),
            models.Index(fields=["distance_parsecs"]),
        ]


class Galaxy(CelestialObject):
    MORPHOLOGY_TYPES = [
        ("spiral", "Spiral"),
        ("barred_spiral", "Barred Spiral"),
        ("elliptical", "Elliptical"),
        ("lenticular", "Lenticular"),
        ("irregular", "Irregular"),
        ("dwarf_elliptical", "Dwarf Elliptical"),
        ("dwarf_spheroidal", "Dwarf Spheroidal"),
        ("dwarf_irregular", "Dwarf Irregular"),
        ("unknown", "Unknown"),
    ]

    morphology = models.CharField(
        max_length=20, choices=MORPHOLOGY_TYPES, default="unknown",
    )
    hubble_type = models.CharField(
        max_length=20, blank=True, default="",
        help_text="Hubble sequence classification (e.g., Sa, SBb, E3)",
    )

    apparent_magnitude = models.FloatField(null=True, blank=True)
    absolute_magnitude = models.FloatField(null=True, blank=True)
    redshift = models.FloatField(null=True, blank=True)
    angular_size_arcmin = models.FloatField(null=True, blank=True)
    mass_solar = models.FloatField(null=True, blank=True)
    diameter_kpc = models.FloatField(null=True, blank=True)
    num_stars_estimate = models.BigIntegerField(null=True, blank=True)

    galaxy_group = models.CharField(max_length=100, blank=True, default="")

    messier_number = models.CharField(max_length=10, blank=True, default="")
    ngc_number = models.CharField(max_length=20, blank=True, default="")
    ic_number = models.CharField(max_length=20, blank=True, default="")

    class Meta:
        verbose_name_plural = "galaxies"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["morphology"]),
            models.Index(fields=["distance_parsecs"]),
            models.Index(fields=["apparent_magnitude"]),
        ]
