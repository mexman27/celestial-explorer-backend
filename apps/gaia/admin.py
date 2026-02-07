from django.contrib import admin

from .models import Star, Planet, Galaxy


@admin.register(Star)
class StarAdmin(admin.ModelAdmin):
    list_display = [
        "name", "catalog_id", "spectral_class",
        "apparent_magnitude", "distance_parsecs", "constellation",
    ]
    list_filter = ["spectral_class", "constellation"]
    search_fields = ["name", "catalog_id", "bayer_designation", "hipparcos_id"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Planet)
class PlanetAdmin(admin.ModelAdmin):
    list_display = [
        "name", "catalog_id", "planet_type",
        "is_exoplanet", "host_star_name", "discovery_year",
    ]
    list_filter = ["planet_type", "is_exoplanet", "detection_method"]
    search_fields = ["name", "catalog_id", "host_star_name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Galaxy)
class GalaxyAdmin(admin.ModelAdmin):
    list_display = [
        "name", "catalog_id", "morphology",
        "apparent_magnitude", "distance_parsecs", "galaxy_group",
    ]
    list_filter = ["morphology", "galaxy_group"]
    search_fields = ["name", "catalog_id", "messier_number", "ngc_number"]
    readonly_fields = ["created_at", "updated_at"]
