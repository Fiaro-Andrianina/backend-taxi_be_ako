from django.contrib import admin

from .models import Paiement


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ["id", "reservation", "montant", "methode", "statut", "cree_le", "paye_le"]
    list_filter = ["methode", "statut", "cree_le"]
    search_fields = ["reference", "reservation__depart__nom", "reservation__arrivee__nom"]
    autocomplete_fields = ["reservation"]
