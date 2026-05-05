from django.urls import path

from . import views


urlpatterns = [
    path("paiements/", views.paiements, name="paiements"),
    path("paiements/<int:pk>/", views.paiement_detail, name="paiement-detail"),
    path("paiements/<int:pk>/valider/", views.valider_paiement, name="valider-paiement"),
]
