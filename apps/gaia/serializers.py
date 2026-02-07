from rest_framework import serializers

from .models import Star, Planet, Galaxy


# --- Stars ---

class StarListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Star
        fields = [
            "id", "name", "catalog_id",
            "right_ascension", "declination", "distance_parsecs",
            "apparent_magnitude", "absolute_magnitude",
            "spectral_type", "spectral_class",
            "temperature_kelvin", "constellation",
            "x_parsecs", "y_parsecs", "z_parsecs",
        ]


class StarDetailSerializer(serializers.ModelSerializer):
    planets = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Star
        fields = "__all__"


# --- Planets ---

class PlanetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planet
        fields = [
            "id", "name", "catalog_id",
            "right_ascension", "declination", "distance_parsecs",
            "planet_type", "is_exoplanet",
            "host_star_name", "host_star_id",
            "mass_earth", "radius_earth",
            "orbital_period_days", "semi_major_axis_au",
            "discovery_year", "detection_method",
            "x_parsecs", "y_parsecs", "z_parsecs",
        ]


class PlanetDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planet
        fields = "__all__"


# --- Galaxies ---

class GalaxyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Galaxy
        fields = [
            "id", "name", "catalog_id",
            "right_ascension", "declination", "distance_parsecs",
            "morphology", "hubble_type",
            "apparent_magnitude", "redshift",
            "angular_size_arcmin", "galaxy_group",
            "messier_number", "ngc_number",
            "x_parsecs", "y_parsecs", "z_parsecs",
        ]


class GalaxyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Galaxy
        fields = "__all__"
