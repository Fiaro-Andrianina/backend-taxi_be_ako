from django.http import JsonResponse

from transport.models import Arret, Ligne, TrajetHistorique


def accueil(request):
    return JsonResponse(
        {
            "service": "Taxi be Ako",
            "version": "1.0",
            "endpoints": {
                "transport": "/api/",
                "accounts": "/api/accounts/",
                "booking": "/api/booking/",
                "payments": "/api/payments/",
            },
        }
    )


def health(request):
    return JsonResponse({"status": "ok", "service": "taxi_be_ako"})


def statistiques(request):
    from reservations.models import Reservation
    from paiements.models import Paiement

    return JsonResponse(
        {
            "lignes": Ligne.objects.count(),
            "arrets": Arret.objects.count(),
            "trajets_recherches": TrajetHistorique.objects.count(),
            "reservations": Reservation.objects.count(),
            "paiements": Paiement.objects.count(),
        }
    )
