from django.contrib.auth.models import User
from django.utils.dateparse import parse_datetime

from comptes.serializers import user_to_dict
from transport.models import Arret
from transport.serializers import arret_to_dict, historique_to_dict
from transport.services import AlgorithmeRecherche

from .models import Reservation


def reservation_to_dict(reservation):
    paiement = getattr(reservation, "paiement", None)
    return {
        "id": reservation.id,
        "utilisateur": user_to_dict(reservation.utilisateur) if reservation.utilisateur else None,
        "depart": arret_to_dict(reservation.depart),
        "arrivee": arret_to_dict(reservation.arrivee),
        "trajet": historique_to_dict(reservation.trajet) if reservation.trajet else None,
        "statut": reservation.statut,
        "nb_passagers": reservation.nb_passagers,
        "prix_estime": float(reservation.prix_estime),
        "date_trajet": reservation.date_trajet.isoformat() if reservation.date_trajet else None,
        "notes": reservation.notes,
        "paiement_id": paiement.id if paiement else None,
        "cree_le": reservation.cree_le.isoformat(),
        "mis_a_jour_le": reservation.mis_a_jour_le.isoformat(),
    }


def creer_reservation(payload):
    depart_id = payload.get("depart", payload.get("dep"))
    arrivee_id = payload.get("arrivee", payload.get("arr"))
    if depart_id is None or arrivee_id is None:
        raise ValueError("Les champs depart/arrivee sont obligatoires")
    if int(depart_id) == int(arrivee_id):
        raise ValueError("Le depart et l'arrivee doivent etre differents")

    utilisateur = None
    utilisateur_id = payload.get("utilisateur") or payload.get("utilisateur_id")
    if utilisateur_id:
        utilisateur = User.objects.get(pk=utilisateur_id)

    depart = Arret.objects.get(pk=depart_id)
    arrivee = Arret.objects.get(pk=arrivee_id)
    resultat = AlgorithmeRecherche().calculer_trajet(depart.id, arrivee.id)
    trajet = resultat["historique"]

    prix_estime = payload.get("prix_estime")
    if prix_estime is None:
        prix_estime = round(resultat["distance_km"] * 1000)

    return Reservation.objects.create(
        utilisateur=utilisateur,
        depart=depart,
        arrivee=arrivee,
        trajet=trajet,
        nb_passagers=payload.get("nb_passagers", 1),
        prix_estime=prix_estime,
        date_trajet=parse_datetime(payload["date_trajet"]) if payload.get("date_trajet") else None,
        notes=payload.get("notes", ""),
    )
