from django.db import models

from reservations.models import Reservation


class Paiement(models.Model):
    METHODE_ESPECES = "especes"
    METHODE_MOBILE_MONEY = "mobile_money"
    METHODE_CARTE = "carte"

    METHODE_CHOICES = [
        (METHODE_ESPECES, "Especes"),
        (METHODE_MOBILE_MONEY, "Mobile Money"),
        (METHODE_CARTE, "Carte bancaire"),
    ]

    STATUT_EN_ATTENTE = "en_attente"
    STATUT_PAYE = "paye"
    STATUT_ECHOUE = "echoue"
    STATUT_REMBOURSE = "rembourse"

    STATUT_CHOICES = [
        (STATUT_EN_ATTENTE, "En attente"),
        (STATUT_PAYE, "Paye"),
        (STATUT_ECHOUE, "Echoue"),
        (STATUT_REMBOURSE, "Rembourse"),
    ]

    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name="paiement",
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    methode = models.CharField(max_length=30, choices=METHODE_CHOICES, default=METHODE_ESPECES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default=STATUT_EN_ATTENTE)
    reference = models.CharField(max_length=100, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    paye_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "paiement"
        ordering = ["-cree_le"]

    def __str__(self):
        return f"Paiement #{self.id} - Reservation #{self.reservation_id}"

    def marquer_paye(self, reference=""):
        from django.utils import timezone

        self.statut = self.STATUT_PAYE
        if reference:
            self.reference = reference
        self.paye_le = timezone.now()
        self.save(update_fields=["statut", "reference", "paye_le"])

    def est_valide(self):
        return self.statut == self.STATUT_PAYE
