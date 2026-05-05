from django.contrib import admin

from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ["id", "utilisateur", "depart", "arrivee", "statut", "prix_estime", "cree_le"]
    list_filter = ["statut", "cree_le"]
    search_fields = ["utilisateur__username", "depart__nom", "arrivee__nom"]
    autocomplete_fields = ["utilisateur", "depart", "arrivee", "trajet"]
