from django.conf import settings
from django.db import models

from transport.models import Arret, TrajetHistorique


class Reservation(models.Model):
    STATUT_EN_ATTENTE = "en_attente"
    STATUT_CONFIRMEE = "confirmee"
    STATUT_ANNULEE = "annulee"
    STATUT_TERMINEE = "terminee"

    STATUT_CHOICES = [
        (STATUT_EN_ATTENTE, "En attente"),
        (STATUT_CONFIRMEE, "Confirmee"),
        (STATUT_ANNULEE, "Annulee"),
        (STATUT_TERMINEE, "Terminee"),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations_taxi",
        null=True,
        blank=True,
    )
    depart = models.ForeignKey(Arret, on_delete=models.PROTECT, related_name="reservations_depart", to_field="id")
    arrivee = models.ForeignKey(Arret, on_delete=models.PROTECT, related_name="reservations_arrivee", to_field="id")
    trajet = models.ForeignKey(
        TrajetHistorique,
        on_delete=models.SET_NULL,
        related_name="reservations",
        null=True,
        blank=True,
    )
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default=STATUT_EN_ATTENTE)
    nb_passagers = models.PositiveIntegerField(default=1)
    prix_estime = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_trajet = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reservation"
        ordering = ["-cree_le"]

    def __str__(self):
        return f"Reservation #{self.id}: {self.depart.nom} -> {self.arrivee.nom}"

    def confirmer(self):
        self.statut = self.STATUT_CONFIRMEE
        self.save(update_fields=["statut", "mis_a_jour_le"])

    def annuler(self):
        self.statut = self.STATUT_ANNULEE
        self.save(update_fields=["statut", "mis_a_jour_le"])

    def est_active(self):
        return self.statut in [self.STATUT_EN_ATTENTE, self.STATUT_CONFIRMEE]
