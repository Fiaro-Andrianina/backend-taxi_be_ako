import secrets
import string

from django.contrib.auth.models import User

from .models import ProfilUtilisateur


def user_to_dict(user):
    profil = getattr(user, "profil_taxi", None)
    return {
        "id": user.id,
        "username": user.username,
        "nom": user.get_full_name().strip() or user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "profil": profil_to_dict(profil) if profil else None,
    }


def profil_to_dict(profil):
    return {
        "id": profil.id,
        "user_id": profil.user_id,
        "telephone": profil.telephone,
        "role": profil.role,
        "adresse": profil.adresse,
        "date_creation": profil.date_creation.isoformat(),
    }


def make_random_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def creer_utilisateur(payload):
    username = payload.get("username") or payload.get("email")
    email = payload.get("email", "")
    password = payload.get("password") or make_random_password()

    if not username:
        raise ValueError("Le champ username ou email est obligatoire")
    if User.objects.filter(username=username).exists():
        raise ValueError("Ce nom d'utilisateur existe deja")

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=payload.get("first_name", payload.get("prenom", "")),
        last_name=payload.get("last_name", payload.get("nom", "")),
    )
    ProfilUtilisateur.objects.create(
        user=user,
        telephone=payload.get("telephone", ""),
        role=payload.get("role", ProfilUtilisateur.ROLE_CLIENT),
        adresse=payload.get("adresse", ""),
    )
    return user
