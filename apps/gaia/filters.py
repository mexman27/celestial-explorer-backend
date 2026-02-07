import django_filters

from .models import Star, Planet, Galaxy


class StarFilter(django_filters.FilterSet):
    min_magnitude = django_filters.NumberFilter(
        field_name="apparent_magnitude", lookup_expr="gte",
    )
    max_magnitude = django_filters.NumberFilter(
        field_name="apparent_magnitude", lookup_expr="lte",
    )
    max_distance = django_filters.NumberFilter(
        field_name="distance_parsecs", lookup_expr="lte",
    )
    constellation = django_filters.CharFilter(
        field_name="constellation", lookup_expr="iexact",
    )

    class Meta:
        model = Star
        fields = ["spectral_class", "constellation"]


class PlanetFilter(django_filters.FilterSet):
    max_distance = django_filters.NumberFilter(
        field_name="distance_parsecs", lookup_expr="lte",
    )
    min_mass_earth = django_filters.NumberFilter(
        field_name="mass_earth", lookup_expr="gte",
    )
    max_mass_earth = django_filters.NumberFilter(
        field_name="mass_earth", lookup_expr="lte",
    )

    class Meta:
        model = Planet
        fields = ["planet_type", "is_exoplanet", "detection_method"]


class GalaxyFilter(django_filters.FilterSet):
    max_distance = django_filters.NumberFilter(
        field_name="distance_parsecs", lookup_expr="lte",
    )
    morphology = django_filters.MultipleChoiceFilter(
        choices=Galaxy.MORPHOLOGY_TYPES,
    )

    class Meta:
        model = Galaxy
        fields = ["morphology", "galaxy_group"]
