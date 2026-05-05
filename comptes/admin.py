from django.contrib import admin

from .models import ProfilUtilisateur


@admin.register(ProfilUtilisateur)
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "telephone", "date_creation"]
    list_filter = ["role"]
    search_fields = ["user__username", "user__email", "telephone"]
