from django.db.models import Count, Avg, Min, Max, Q
from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import Star, Planet, Galaxy
from .serializers import (
    StarListSerializer, StarDetailSerializer,
    PlanetListSerializer, PlanetDetailSerializer,
    GalaxyListSerializer, GalaxyDetailSerializer,
)
from .filters import StarFilter, PlanetFilter, GalaxyFilter


# --- Stars ---

class StarListView(generics.ListAPIView):
    queryset = Star.objects.all()
    serializer_class = StarListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = StarFilter
    search_fields = ["name", "catalog_id", "bayer_designation", "constellation"]
    ordering_fields = [
        "name", "apparent_magnitude", "absolute_magnitude",
        "distance_parsecs", "temperature_kelvin",
    ]
    ordering = ["apparent_magnitude"]


class StarDetailView(generics.RetrieveAPIView):
    queryset = Star.objects.all()
    serializer_class = StarDetailSerializer


class StarStatsView(APIView):
    def get(self, request):
        stats = Star.objects.aggregate(
            total=Count("id"),
            avg_distance=Avg("distance_parsecs"),
            min_magnitude=Min("apparent_magnitude"),
            max_magnitude=Max("apparent_magnitude"),
        )
        by_spectral_class = list(
            Star.objects.values("spectral_class")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        stats["by_spectral_class"] = by_spectral_class
        return Response(stats)


# --- Planets ---

class PlanetListView(generics.ListAPIView):
    queryset = Planet.objects.all()
    serializer_class = PlanetListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PlanetFilter
    search_fields = ["name", "catalog_id", "host_star_name"]
    ordering_fields = [
        "name", "distance_parsecs", "mass_earth",
        "orbital_period_days", "discovery_year",
    ]
    ordering = ["name"]


class PlanetDetailView(generics.RetrieveAPIView):
    queryset = Planet.objects.all()
    serializer_class = PlanetDetailSerializer


class PlanetStatsView(APIView):
    def get(self, request):
        stats = Planet.objects.aggregate(
            total=Count("id"),
            exoplanets=Count("id", filter=Q(is_exoplanet=True)),
            avg_distance=Avg("distance_parsecs"),
        )
        by_type = list(
            Planet.objects.values("planet_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        by_detection = list(
            Planet.objects.values("detection_method")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        stats["by_type"] = by_type
        stats["by_detection_method"] = by_detection
        return Response(stats)


# --- Galaxies ---

class GalaxyListView(generics.ListAPIView):
    queryset = Galaxy.objects.all()
    serializer_class = GalaxyListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = GalaxyFilter
    search_fields = ["name", "catalog_id", "messier_number", "ngc_number"]
    ordering_fields = [
        "name", "distance_parsecs", "apparent_magnitude", "redshift",
    ]
    ordering = ["name"]


class GalaxyDetailView(generics.RetrieveAPIView):
    queryset = Galaxy.objects.all()
    serializer_class = GalaxyDetailSerializer


class GalaxyStatsView(APIView):
    def get(self, request):
        stats = Galaxy.objects.aggregate(
            total=Count("id"),
            avg_distance=Avg("distance_parsecs"),
        )
        by_morphology = list(
            Galaxy.objects.values("morphology")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        stats["by_morphology"] = by_morphology
        return Response(stats)
