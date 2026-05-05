from reservations.models import Reservation
from reservations.serializers import reservation_to_dict

from .models import Paiement


def paiement_to_dict(paiement):
    return {
        "id": paiement.id,
        "reservation": reservation_to_dict(paiement.reservation),
        "montant": float(paiement.montant),
        "methode": paiement.methode,
        "statut": paiement.statut,
        "reference": paiement.reference,
        "cree_le": paiement.cree_le.isoformat(),
        "paye_le": paiement.paye_le.isoformat() if paiement.paye_le else None,
    }


def creer_paiement(payload):
    reservation_id = payload.get("reservation") or payload.get("reservation_id")
    if not reservation_id:
        raise ValueError("Le champ reservation est obligatoire")

    reservation = Reservation.objects.get(pk=reservation_id)
    montant = payload.get("montant", reservation.prix_estime)

    if Paiement.objects.filter(reservation=reservation).exists():
        raise ValueError("Un paiement existe deja pour cette reservation")

    return Paiement.objects.create(
        reservation=reservation,
        montant=montant,
        methode=payload.get("methode", Paiement.METHODE_ESPECES),
        statut=payload.get("statut", Paiement.STATUT_EN_ATTENTE),
        reference=payload.get("reference", ""),
    )
