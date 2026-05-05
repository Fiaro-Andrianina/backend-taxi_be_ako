import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from transport.models import Arret
from transport.services import TrajetIntrouvable

from .models import Reservation
from .serializers import creer_reservation, reservation_to_dict


@csrf_exempt
def reservations(request):
    if request.method == "GET":
        queryset = Reservation.objects.select_related(
            "utilisateur", "depart", "arrivee", "trajet"
        ).prefetch_related("trajet__lignes", "trajet__correspondances")
        return JsonResponse([reservation_to_dict(item) for item in queryset], safe=False)

    if request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
            reservation = creer_reservation(payload)
        except json.JSONDecodeError:
            return JsonResponse({"detail": "JSON invalide"}, status=400)
        except (ValueError, User.DoesNotExist, Arret.DoesNotExist) as exc:
            return JsonResponse({"detail": str(exc)}, status=400)
        except TrajetIntrouvable as exc:
            return JsonResponse({"detail": str(exc)}, status=404)

        return JsonResponse(reservation_to_dict(reservation), status=201)

    return JsonResponse({"detail": "Methode non autorisee"}, status=405)


@csrf_exempt
def reservation_detail(request, pk):
    try:
        reservation = Reservation.objects.select_related(
            "utilisateur", "depart", "arrivee", "trajet"
        ).get(pk=pk)
    except Reservation.DoesNotExist:
        return JsonResponse({"detail": "Reservation introuvable"}, status=404)

    if request.method == "GET":
        return JsonResponse(reservation_to_dict(reservation))

    if request.method in ["PUT", "PATCH"]:
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"detail": "JSON invalide"}, status=400)

        if "utilisateur" in payload or "utilisateur_id" in payload:
            reservation.utilisateur_id = payload.get("utilisateur", payload.get("utilisateur_id"))
        reservation.depart_id = payload.get("depart", payload.get("dep", reservation.depart_id))
        reservation.arrivee_id = payload.get("arrivee", payload.get("arr", reservation.arrivee_id))
        reservation.statut = payload.get("statut", reservation.statut)
        reservation.nb_passagers = payload.get("nb_passagers", reservation.nb_passagers)
        reservation.prix_estime = payload.get("prix_estime", reservation.prix_estime)
        reservation.notes = payload.get("notes", reservation.notes)
        reservation.save()
        return JsonResponse(reservation_to_dict(reservation))

    if request.method == "DELETE":
        reservation.delete()
        return JsonResponse({"detail": "Reservation supprimee"})

    return JsonResponse({"detail": "Methode non autorisee"}, status=405)


@csrf_exempt
def confirmer_reservation(request, pk):
    if request.method != "POST":
        return JsonResponse({"detail": "Methode non autorisee"}, status=405)
    try:
        reservation = Reservation.objects.get(pk=pk)
    except Reservation.DoesNotExist:
        return JsonResponse({"detail": "Reservation introuvable"}, status=404)
    reservation.confirmer()
    return JsonResponse(reservation_to_dict(reservation))


@csrf_exempt
def annuler_reservation(request, pk):
    if request.method != "POST":
        return JsonResponse({"detail": "Methode non autorisee"}, status=405)
    try:
        reservation = Reservation.objects.get(pk=pk)
    except Reservation.DoesNotExist:
        return JsonResponse({"detail": "Reservation introuvable"}, status=404)
    reservation.annuler()
    return JsonResponse(reservation_to_dict(reservation))
