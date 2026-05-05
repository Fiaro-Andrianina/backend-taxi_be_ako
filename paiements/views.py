import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from reservations.models import Reservation

from .models import Paiement
from .serializers import creer_paiement, paiement_to_dict


@csrf_exempt
def paiements(request):
    if request.method == "GET":
        queryset = Paiement.objects.select_related(
            "reservation", "reservation__depart", "reservation__arrivee"
        )
        return JsonResponse([paiement_to_dict(item) for item in queryset], safe=False)

    if request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
            paiement = creer_paiement(payload)
        except json.JSONDecodeError:
            return JsonResponse({"detail": "JSON invalide"}, status=400)
        except (ValueError, Reservation.DoesNotExist) as exc:
            return JsonResponse({"detail": str(exc)}, status=400)

        return JsonResponse(paiement_to_dict(paiement), status=201)

    return JsonResponse({"detail": "Methode non autorisee"}, status=405)


@csrf_exempt
def paiement_detail(request, pk):
    try:
        paiement = Paiement.objects.select_related("reservation").get(pk=pk)
    except Paiement.DoesNotExist:
        return JsonResponse({"detail": "Paiement introuvable"}, status=404)

    if request.method == "GET":
        return JsonResponse(paiement_to_dict(paiement))

    if request.method in ["PUT", "PATCH"]:
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"detail": "JSON invalide"}, status=400)

        paiement.reservation_id = payload.get("reservation", payload.get("reservation_id", paiement.reservation_id))
        paiement.montant = payload.get("montant", paiement.montant)
        paiement.methode = payload.get("methode", paiement.methode)
        paiement.statut = payload.get("statut", paiement.statut)
        paiement.reference = payload.get("reference", paiement.reference)
        paiement.save()
        return JsonResponse(paiement_to_dict(paiement))

    if request.method == "DELETE":
        paiement.delete()
        return JsonResponse({"detail": "Paiement supprime"})

    return JsonResponse({"detail": "Methode non autorisee"}, status=405)


@csrf_exempt
def valider_paiement(request, pk):
    if request.method != "POST":
        return JsonResponse({"detail": "Methode non autorisee"}, status=405)
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "JSON invalide"}, status=400)

    try:
        paiement = Paiement.objects.select_related("reservation").get(pk=pk)
    except Paiement.DoesNotExist:
        return JsonResponse({"detail": "Paiement introuvable"}, status=404)

    paiement.marquer_paye(reference=payload.get("reference", ""))
    paiement.reservation.confirmer()
    return JsonResponse(paiement_to_dict(paiement))
