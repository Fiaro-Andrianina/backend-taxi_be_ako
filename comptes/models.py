from django.conf import settings
from django.db import models


class ProfilUtilisateur(models.Model):
    ROLE_CLIENT = "client"
    ROLE_CHAUFFEUR = "chauffeur"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = [
        (ROLE_CLIENT, "Client"),
        (ROLE_CHAUFFEUR, "Chauffeur"),
        (ROLE_ADMIN, "Administrateur"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profil_taxi",
    )
    telephone = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CLIENT)
    adresse = models.CharField(max_length=255, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "profil_utilisateur"
        ordering = ["user__username"]

    def __str__(self):
        return self.get_nom()

    def get_id(self):
        return self.user.id

    def get_nom(self):
        nom_complet = self.user.get_full_name().strip()
        return nom_complet or self.user.username

    def get_email(self):
        return self.user.email
