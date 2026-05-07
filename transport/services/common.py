from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt


class TrajetIntrouvable(Exception):
    pass


@dataclass(frozen=True)
class Edge:
    destination_id: int
    ligne_id: int
    distance_km: float


def calculer_distance(arret_a, arret_b):
    """Calcule la distance Haversine entre deux arrêts en km"""
    rayon_terre_km = 6371.0
    lat1, lon1 = radians(arret_a.latitude), radians(arret_a.longitude)
    lat2, lon2 = radians(arret_b.latitude), radians(arret_b.longitude)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    hav = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * rayon_terre_km * asin(sqrt(hav))
