from django.urls import path

from . import views

app_name = "gaia"

urlpatterns = [
    # Stars
    path("stars/", views.StarListView.as_view(), name="star-list"),
    path("stars/<int:pk>/", views.StarDetailView.as_view(), name="star-detail"),
    path("stars/stats/", views.StarStatsView.as_view(), name="star-stats"),
    # Planets
    path("planets/", views.PlanetListView.as_view(), name="planet-list"),
    path("planets/<int:pk>/", views.PlanetDetailView.as_view(), name="planet-detail"),
    path("planets/stats/", views.PlanetStatsView.as_view(), name="planet-stats"),
    # Galaxies
    path("galaxies/", views.GalaxyListView.as_view(), name="galaxy-list"),
    path("galaxies/<int:pk>/", views.GalaxyDetailView.as_view(), name="galaxy-detail"),
    path("galaxies/stats/", views.GalaxyStatsView.as_view(), name="galaxy-stats"),
]
