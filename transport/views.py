import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Arret, Ligne, LigneArret, TrajetHistorique
from .serializers import (
    arret_to_dict,
    graphe_to_dict,
    historique_to_dict,
    ligne_to_dict,
    sync_to_dict,
    trajet_to_dict,
)
from .services import AlgorithmeRecherche, TrajetIntrouvable


def health(request):
    return JsonResponse({"status": "ok", "service": "taxi_be_ako"})


@csrf_exempt
def lignes(request):
    if request.method == "GET":
        return JsonResponse([ligne_to_dict(ligne) for ligne in Ligne.objects.all()], safe=False)

    if request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
            ligne = Ligne.objects.create(
                numero=payload["numero"],
                nom=payload["nom"],
                description=payload.get("description", ""),
            )
        except json.JSONDecodeError:
            return JsonResponse({"detail": "JSON invalide"}, status=400)
        except KeyError as exc:
            return JsonResponse({"detail": f"Champ obligatoire: {exc.args[0]}"}, status=400)
        return JsonResponse(ligne_to_dict(ligne, detail=True), status=201)

    return JsonResponse({"detail": "Methode non autorisee"}, status=405)


@csrf_exempt
def ligne_detail(request, pk):
    try:
        ligne = Ligne.objects.get(pk=pk)
    except Ligne.DoesNotExist:
        return JsonResponse({"detail": "Ligne introuvable"}, status=404)

    if request.method == "GET":
        return JsonResponse(ligne_to_dict(ligne, detail=True))

    if request.method in ["PUT", "PATCH"]:
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"detail": "JSON invalide"}, status=400)
        ligne.numero = payload.get("numero", ligne.numero)
        ligne.nom = payload.get("nom", ligne.nom)
        ligne.description = payload.get("description", ligne.description)
        ligne.save()
        return JsonResponse(ligne_to_dict(ligne, detail=True))

    if request.method == "DELETE":
        ligne.delete()
        return JsonResponse({"detail": "Ligne supprimee"})

    return JsonResponse({"detail": "Methode non autorisee"}, status=405)


def ligne_arrets(request, pk):
    if request.method != "GET":
        return JsonResponse({"detail": "Methode non autorisee"}, status=405)
    arrets = Arret.objects.filter(lignearret__ligne_id=pk).order_by("lignearret__ordre")
    return JsonResponse([arret_to_dict(arret) for arret in arrets], safe=False)


@csrf_exempt
def arrets(request):
    if request.method == "GET":
        queryset = Arret.objects.all()
        ligne_id = request.GET.get("ligne")
        if ligne_id:
            queryset = queryset.filter(lignearret__ligne_id=ligne_id).order_by("lignearret__ordre")
        return JsonResponse([arret_to_dict(arret) for arret in queryset], safe=False)

    if request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
            arret = Arret.objects.create(
                nom=payload["nom"],
                latitude=payload["latitude"],
                longitude=payload["longitude"],
            )
        except json.JSONDecodeError:
            return JsonResponse({"detail": "JSON invalide"}, status=400)
        except KeyError as exc:
            return JsonResponse({"detail": f"Champ obligatoire: {exc.args[0]}"}, status=400)
        return JsonResponse(arret_to_dict(arret), status=201)

    return JsonResponse({"detail": "Methode non autorisee"}, status=405)


@csrf_exempt
def arret_detail(request, pk):
    try:
        arret = Arret.objects.get(pk=pk)
    except Arret.DoesNotExist:
        return JsonResponse({"detail": "Arret introuvable"}, status=404)

    if request.method == "GET":
        return JsonResponse(arret_to_dict(arret))

    if request.method in ["PUT", "PATCH"]:
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"detail": "JSON invalide"}, status=400)
        arret.nom = payload.get("nom", arret.nom)
        arret.latitude = payload.get("latitude", arret.latitude)
        arret.longitude = payload.get("longitude", arret.longitude)
        arret.save()
        return JsonResponse(arret_to_dict(arret))

    if request.method == "DELETE":
        arret.delete()
        return JsonResponse({"detail": "Arret supprime"})

    return JsonResponse({"detail": "Methode non autorisee"}, status=405)


@csrf_exempt
def ligne_arrets_crud(request):
    if request.method == "GET":
        queryset = LigneArret.objects.select_related("ligne", "arret").all()
        return JsonResponse(
            [
                {
                    "id": item.id,
                    "ligne": ligne_to_dict(item.ligne),
                    "arret": arret_to_dict(item.arret),
                    "ordre": item.ordre,
                }
                for item in queryset
            ],
            safe=False,
        )

    if request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
            item = LigneArret.objects.create(
                ligne_id=payload["ligne"],
                arret_id=payload["arret"],
                ordre=payload["ordre"],
            )
        except json.JSONDecodeError:
            return JsonResponse({"detail": "JSON invalide"}, status=400)
        except KeyError as exc:
            return JsonResponse({"detail": f"Champ obligatoire: {exc.args[0]}"}, status=400)
        return JsonResponse({"id": item.id, "ordre": item.ordre}, status=201)

    return JsonResponse({"detail": "Methode non autorisee"}, status=405)


@csrf_exempt
def ligne_arret_detail(request, pk):
    try:
        item = LigneArret.objects.select_related("ligne", "arret").get(pk=pk)
    except LigneArret.DoesNotExist:
        return JsonResponse({"detail": "Association ligne-arret introuvable"}, status=404)

    if request.method == "GET":
        return JsonResponse(
            {
                "id": item.id,
                "ligne": ligne_to_dict(item.ligne),
                "arret": arret_to_dict(item.arret),
                "ordre": item.ordre,
            }
        )

    if request.method in ["PUT", "PATCH"]:
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"detail": "JSON invalide"}, status=400)
        item.ligne_id = payload.get("ligne", item.ligne_id)
        item.arret_id = payload.get("arret", item.arret_id)
        item.ordre = payload.get("ordre", item.ordre)
        item.save()
        return JsonResponse({"id": item.id, "ordre": item.ordre})

    if request.method == "DELETE":
        item.delete()
        return JsonResponse({"detail": "Association ligne-arret supprimee"})

    return JsonResponse({"detail": "Methode non autorisee"}, status=405)


def sync(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Methode non autorisee"}, status=405)
    return JsonResponse(sync_to_dict())


def graphe(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Methode non autorisee"}, status=405)
    data = AlgorithmeRecherche().get_graphe()
    return JsonResponse(graphe_to_dict(data))


@csrf_exempt
def trajet(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Methode non autorisee"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "JSON invalide"}, status=400)

    depart = payload.get("depart", payload.get("dep"))
    arrivee = payload.get("arrivee", payload.get("arr"))
    if depart is None or arrivee is None:
        return JsonResponse({"detail": "Les champs depart/arrivee sont obligatoires"}, status=400)
    if depart == arrivee:
        return JsonResponse({"detail": "Le depart et l'arrivee doivent etre differents"}, status=400)

    try:
        resultat = AlgorithmeRecherche().calculer_trajet(int(depart), int(arrivee))
    except (TypeError, ValueError):
        return JsonResponse({"detail": "depart et arrivee doivent etre des identifiants"}, status=400)
    except TrajetIntrouvable as exc:
        return JsonResponse({"detail": str(exc)}, status=404)

    return JsonResponse(trajet_to_dict(resultat))


def historique_trajets(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Methode non autorisee"}, status=405)
    trajets = TrajetHistorique.objects.select_related("depart", "arrivee").prefetch_related(
        "lignes", "correspondances"
    )
    return JsonResponse([historique_to_dict(item) for item in trajets], safe=False)
