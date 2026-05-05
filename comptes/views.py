import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .serializers import creer_utilisateur, user_to_dict


@csrf_exempt
def utilisateurs(request):
    if request.method == "GET":
        users = User.objects.select_related("profil_taxi").all().order_by("username")
        return JsonResponse([user_to_dict(user) for user in users], safe=False)

    if request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
            user = creer_utilisateur(payload)
        except json.JSONDecodeError:
            return JsonResponse({"detail": "JSON invalide"}, status=400)
        except ValueError as exc:
            return JsonResponse({"detail": str(exc)}, status=400)

        return JsonResponse(user_to_dict(user), status=201)

    return JsonResponse({"detail": "Methode non autorisee"}, status=405)


@csrf_exempt
def utilisateur_detail(request, pk):
    try:
        user = User.objects.select_related("profil_taxi").get(pk=pk)
    except User.DoesNotExist:
        return JsonResponse({"detail": "Utilisateur introuvable"}, status=404)

    if request.method == "GET":
        return JsonResponse(user_to_dict(user))

    if request.method in ["PUT", "PATCH"]:
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"detail": "JSON invalide"}, status=400)

        user.username = payload.get("username", user.username)
        user.email = payload.get("email", user.email)
        user.first_name = payload.get("first_name", payload.get("prenom", user.first_name))
        user.last_name = payload.get("last_name", payload.get("nom", user.last_name))
        if payload.get("password"):
            user.set_password(payload["password"])
        user.save()

        profil = getattr(user, "profil_taxi", None)
        if profil:
            profil.telephone = payload.get("telephone", profil.telephone)
            profil.role = payload.get("role", profil.role)
            profil.adresse = payload.get("adresse", profil.adresse)
            profil.save()

        return JsonResponse(user_to_dict(user))

    if request.method == "DELETE":
        user.delete()
        return JsonResponse({"detail": "Utilisateur supprime"})

    return JsonResponse({"detail": "Methode non autorisee"}, status=405)
