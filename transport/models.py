from typing import cast

from django.db import models
from django.db.models import Min


class Arret(models.Model):
    id: int  # type: ignore[assignment]
    nom = models.CharField(max_length=120, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        db_table = "arret"
        ordering = ["nom"]
        verbose_name = "arret"
        verbose_name_plural = "arrets"

    def __str__(self):
        return self.nom

    def get_nom(self):
        return self.nom

    def get_coords(self):
        return (self.latitude, self.longitude)

    def est_correspondance(self):
        return self.lignes.count() > 1  # type: ignore[attr-defined]


class Ligne(models.Model):
    id: int  # type: ignore[assignment]
    numero = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    arrets = models.ManyToManyField(Arret, through="LigneArret", related_name="lignes")

    class Meta:
        db_table = "ligne"
        ordering = ["numero", "nom"]

    def __str__(self):
        return f"{self.numero} - {self.nom}"

    def get_arrets(self):
        return Arret.objects.filter(lignearret__ligne=self).order_by("lignearret__ordre")

    def get_terminus(self):
        arrets = list(self.get_arrets())
        if not arrets:
            return []
        if len(arrets) == 1:
            return [arrets[0]]
        return [arrets[0], arrets[-1]]

    def contient_arret(self, arret):
        return self.arrets.filter(pk=arret.pk).exists()

    def get_nb_arrets(self):
        return self.arrets.count()


class LigneArret(models.Model):
    id: int  # type: ignore[assignment]
    ligne_id: int  # type: ignore[assignment]
    arret_id: int  # type: ignore[assignment]
    ligne = models.ForeignKey(Ligne, on_delete=models.CASCADE)
    arret = models.ForeignKey(Arret, on_delete=models.CASCADE)
    ordre = models.PositiveIntegerField()

    class Meta:
        db_table = "ligne_arret"
        ordering = ["ligne__numero", "ordre"]
        constraints = [
            models.UniqueConstraint(fields=["ligne", "arret"], name="unique_ligne_arret"),
            models.UniqueConstraint(fields=["ligne", "ordre"], name="unique_ordre_par_ligne"),
        ]

    def __str__(self):
        return f"{self.ligne.numero} - {self.ordre}. {self.arret.nom}"

    def get_ordre(self):
        return self.ordre

    def get_arret(self):
        return self.arret

    def get_ligne(self):
        return self.ligne


class Correspondance(models.Model):
    ligne_depart_id: int  # type: ignore[assignment]
    ligne_arrivee_id: int  # type: ignore[assignment]
    arret = models.ForeignKey(Arret, on_delete=models.CASCADE, related_name="correspondances")
    ligne_depart = models.ForeignKey(
        Ligne, on_delete=models.CASCADE, related_name="correspondances_depart"
    )
    ligne_arrivee = models.ForeignKey(
        Ligne, on_delete=models.CASCADE, related_name="correspondances_arrivee"
    )
    temps_estime_minutes = models.PositiveIntegerField(default=5)

    class Meta:
        db_table = "correspondance"
        ordering = ["arret__nom", "ligne_depart__numero", "ligne_arrivee__numero"]
        constraints = [
            models.UniqueConstraint(
                fields=["arret", "ligne_depart", "ligne_arrivee"],
                name="unique_correspondance",
            )
        ]

    def __str__(self):
        return f"{self.arret.nom}: {self.ligne_depart.numero} -> {self.ligne_arrivee.numero}"

    def get_arret_changement(self):
        return self.arret

    def get_lignes(self):
        return [self.ligne_depart, self.ligne_arrivee]

    def est_valide(self):
        return (
            self.ligne_depart_id != self.ligne_arrivee_id
            and self.ligne_depart.contient_arret(self.arret)
            and self.ligne_arrivee.contient_arret(self.arret)
        )


class TrajetHistorique(models.Model):
    depart = models.ForeignKey(Arret, on_delete=models.PROTECT, related_name="trajets_depart")
    arrivee = models.ForeignKey(Arret, on_delete=models.PROTECT, related_name="trajets_arrivee")
    lignes = models.ManyToManyField(Ligne, blank=True, related_name="trajets")
    correspondances = models.ManyToManyField(Correspondance, blank=True, related_name="trajets")
    nb_changements = models.PositiveIntegerField(default=0)
    duree_minutes = models.PositiveIntegerField(default=0)
    distance_km = models.FloatField(default=0)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "trajet_historique"
        ordering = ["-cree_le"]

    def __str__(self):
        return f"{self.depart.nom} -> {self.arrivee.nom}"

    def get_duree(self):
        return self.duree_minutes

    def afficher_itineraire(self):
        lignes = " -> ".join(ligne.numero for ligne in self.lignes.all())
        return f"{self.depart.nom} -> {self.arrivee.nom} ({lignes})"

    def est_optimal(self):
        best = TrajetHistorique.objects.aggregate(best=Min("duree_minutes"))["best"]
        return best is None or self.duree_minutes <= best
