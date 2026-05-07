from heapq import heappop, heappush

from ..models import Arret, Correspondance, Ligne, LigneArret, TrajetHistorique
from .baseline import AlgorithmeSearchBaseline
from .common import Edge, TrajetIntrouvable, calculer_distance


class AlgorithmeSearchOptimized(AlgorithmeSearchBaseline):
    """Version optimisée avec Dijkstra - optimal pour trajets long distance"""

    def dijkstra(self, start_id, end_id):
        """Algorithme de Dijkstra - trouve le chemin le plus court en distance"""
        distances = {start_id: 0.0}
        parents = {}
        heap = [(0.0, start_id)]

        while heap:
            distance_courante, courant = heappop(heap)
            if courant == end_id:
                return self._reconstruire_chemin(parents, start_id, end_id)
            if distance_courante > distances.get(courant, float("inf")):
                continue

            for edge in self.graphe.get(courant, []):
                nouvelle_distance = distance_courante + edge.distance_km
                if nouvelle_distance < distances.get(edge.destination_id, float("inf")):
                    distances[edge.destination_id] = nouvelle_distance
                    parents[edge.destination_id] = (courant, edge)
                    heappush(heap, (nouvelle_distance, edge.destination_id))

        raise TrajetIntrouvable("Aucun trajet disponible")

    def _reconstruire_chemin(self, parents, start_id, end_id):
        courant = end_id
        chemin = []
        while courant != start_id:
            if courant not in parents:
                raise TrajetIntrouvable("Aucun trajet disponible")
            precedent, edge = parents[courant]
            chemin.append(edge)
            courant = precedent
        chemin.reverse()
        return chemin

    def calculer_trajet(self, depart_id, arrivee_id):
        """Calcule un trajet optimisé en utilisant Dijkstra"""
        if depart_id not in self.arrets or arrivee_id not in self.arrets:
            raise TrajetIntrouvable("Arret introuvable")

        chemin = self.dijkstra(depart_id, arrivee_id)
        if not chemin:
            raise TrajetIntrouvable("Aucun trajet disponible")

        arret_ids = [depart_id] + [edge.destination_id for edge in chemin]
        ligne_ids = []
        for edge in chemin:
            if edge.ligne_id not in ligne_ids:
                ligne_ids.append(edge.ligne_id)

        distance_km = round(sum(edge.distance_km for edge in chemin), 2)
        correspondances = self.trouver_correspondances(chemin)
        duree_minutes = max(1, round(distance_km * 3 + len(correspondances) * 5))

        historique = TrajetHistorique.objects.create(
            depart_id=depart_id,
            arrivee_id=arrivee_id,
            nb_changements=len(correspondances),
            duree_minutes=duree_minutes,
            distance_km=distance_km,
        )
        historique.lignes.set(ligne_ids)
        historique.correspondances.set(correspondances)

        return {
            "depart": self.arrets[depart_id],
            "arrivee": self.arrets[arrivee_id],
            "arrets": self._etapes(arret_ids, chemin),
            "lignes": [self.lignes[ligne_id] for ligne_id in ligne_ids],
            "correspondances": correspondances,
            "historique": historique,
            "nb_changements": len(correspondances),
            "duree_minutes": duree_minutes,
            "distance_km": distance_km,
        }
