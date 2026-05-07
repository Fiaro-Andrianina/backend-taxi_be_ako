from collections import deque

from ..models import Arret, Correspondance, Ligne, LigneArret, TrajetHistorique
from .common import Edge, TrajetIntrouvable, calculer_distance


class AlgorithmeSearchBaseline:
    """Version baseline avec BFS - simple et rapide pour petits graphes"""

    def __init__(self) -> None:
        self.arrets: dict[int, Arret] = {arret.id: arret for arret in Arret.objects.all()}
        self.lignes: dict[int, Ligne] = {ligne.id: ligne for ligne in Ligne.objects.all()}
        self.graphe = self.construire_graphe()

    def construire_graphe(self):
        graphe = {arret_id: [] for arret_id in self.arrets}
        lignes_arrets = LigneArret.objects.select_related("ligne", "arret").order_by(
            "ligne_id", "ordre"
        )

        par_ligne: dict[int, list[LigneArret]] = {}
        for item in lignes_arrets:
            par_ligne.setdefault(item.ligne_id, []).append(item)

        for ligne_id, sequence in par_ligne.items():
            for index in range(len(sequence) - 1):
                depart = sequence[index].arret
                arrivee = sequence[index + 1].arret
                distance = calculer_distance(depart, arrivee)
                graphe[depart.id].append(Edge(arrivee.id, ligne_id, distance))
                graphe[arrivee.id].append(Edge(depart.id, ligne_id, distance))

        return graphe

    def get_graphe(self):
        aretes = []
        deja_vues = set()

        for depart_id, edges in self.graphe.items():
            for edge in edges:
                cle = tuple(sorted([depart_id, edge.destination_id])) + (edge.ligne_id,)
                if cle in deja_vues:
                    continue
                deja_vues.add(cle)
                aretes.append(
                    {
                        "depart": self.arrets[depart_id],
                        "arrivee": self.arrets[edge.destination_id],
                        "ligne": self.lignes[edge.ligne_id],
                        "distance_km": round(edge.distance_km, 2),
                    }
                )

        return {
            "noeuds": list(self.arrets.values()),
            "aretes": aretes,
        }

    def bfs(self, start_id, end_id):
        """Recherche en largeur - trouve le chemin le plus court en nombre d'étapes"""
        queue = deque([(start_id, [])])
        visites = {start_id}

        while queue:
            courant, chemin = queue.popleft()
            if courant == end_id:
                return chemin

            for edge in self.graphe.get(courant, []):
                if edge.destination_id not in visites:
                    visites.add(edge.destination_id)
                    queue.append((edge.destination_id, chemin + [edge]))

        raise TrajetIntrouvable("Aucun trajet disponible")

    def trouver_correspondances(self, chemin):
        correspondances = []
        for previous, current in zip(chemin, chemin[1:]):
            if previous.ligne_id == current.ligne_id:
                continue
            correspondance, _ = Correspondance.objects.get_or_create(
                arret_id=previous.destination_id,
                ligne_depart_id=previous.ligne_id,
                ligne_arrivee_id=current.ligne_id,
                defaults={"temps_estime_minutes": 5},
            )
            correspondances.append(correspondance)
        return correspondances

    def calculer_trajet(self, depart_id, arrivee_id):
        """Calcule un trajet en utilisant BFS"""
        if depart_id not in self.arrets or arrivee_id not in self.arrets:
            raise TrajetIntrouvable("Arret introuvable")

        chemin = self.bfs(depart_id, arrivee_id)
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

    def _etapes(self, arret_ids, chemin):
        etapes = []
        for index, arret_id in enumerate(arret_ids):
            lignes = []
            if index > 0:
                lignes.append(self.lignes[chemin[index - 1].ligne_id])
            if index < len(chemin) and chemin[index].ligne_id not in [
                ligne.id for ligne in lignes
            ]:
                lignes.append(self.lignes[chemin[index].ligne_id])
            etapes.append({"arret": self.arrets[arret_id], "lignes": lignes})
        return etapes
