from .models import Arret, Correspondance, Ligne, LigneArret, TrajetHistorique


def arret_to_dict(arret):
    return {
        "id": arret.id,
        "nom": arret.nom,
        "latitude": arret.latitude,
        "longitude": arret.longitude,
        "est_correspondance": arret.est_correspondance(),
    }


def ligne_to_dict(ligne, detail=False):
    data = {
        "id": ligne.id,
        "numero": ligne.numero,
        "nom": ligne.nom,
        "description": ligne.description,
        "nb_arrets": ligne.get_nb_arrets(),
    }
    if detail:
        data["arrets"] = [
            ligne_arret_to_dict(item)
            for item in LigneArret.objects.filter(ligne=ligne)
            .select_related("arret")
            .order_by("ordre")
        ]
    return data


def ligne_arret_to_dict(ligne_arret):
    return {
        "id": ligne_arret.id,
        "ordre": ligne_arret.ordre,
        "arret": arret_to_dict(ligne_arret.arret),
    }


def correspondance_to_dict(correspondance):
    return {
        "id": correspondance.id,
        "arret": arret_to_dict(correspondance.arret),
        "ligne_depart": ligne_to_dict(correspondance.ligne_depart),
        "ligne_arrivee": ligne_to_dict(correspondance.ligne_arrivee),
        "temps_estime_minutes": correspondance.temps_estime_minutes,
    }


def etape_to_dict(etape):
    return {
        "arret": arret_to_dict(etape["arret"]),
        "lignes": [ligne_to_dict(ligne) for ligne in etape["lignes"]],
    }


def trajet_to_dict(trajet):
    return {
        "depart": arret_to_dict(trajet["depart"]),
        "arrivee": arret_to_dict(trajet["arrivee"]),
        "arrets": [etape_to_dict(etape) for etape in trajet["arrets"]],
        "lignes": [ligne_to_dict(ligne) for ligne in trajet["lignes"]],
        "correspondances": [
            correspondance_to_dict(correspondance)
            for correspondance in trajet["correspondances"]
        ],
        "nb_changements": trajet["nb_changements"],
        "duree_minutes": trajet["duree_minutes"],
        "distance_km": trajet["distance_km"],
    }


def historique_to_dict(trajet):
    return {
        "id": trajet.id,
        "depart": arret_to_dict(trajet.depart),
        "arrivee": arret_to_dict(trajet.arrivee),
        "lignes": [ligne_to_dict(ligne) for ligne in trajet.lignes.all()],
        "correspondances": [
            correspondance_to_dict(correspondance)
            for correspondance in trajet.correspondances.all()
        ],
        "nb_changements": trajet.nb_changements,
        "duree_minutes": trajet.duree_minutes,
        "distance_km": trajet.distance_km,
        "cree_le": trajet.cree_le.isoformat(),
    }


def graphe_to_dict(graphe):
    return {
        "noeuds": [arret_to_dict(arret) for arret in graphe["noeuds"]],
        "aretes": [
            {
                "depart": arret_to_dict(arete["depart"]),
                "arrivee": arret_to_dict(arete["arrivee"]),
                "ligne": ligne_to_dict(arete["ligne"]),
                "distance_km": arete["distance_km"],
            }
            for arete in graphe["aretes"]
        ],
    }


def sync_to_dict():
    return {
        "lignes": [ligne_to_dict(ligne, detail=True) for ligne in Ligne.objects.all()],
        "arrets": [arret_to_dict(arret) for arret in Arret.objects.all()],
        "correspondances": [
            correspondance_to_dict(correspondance)
            for correspondance in Correspondance.objects.select_related(
                "arret", "ligne_depart", "ligne_arrivee"
            )
        ],
    }
