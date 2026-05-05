from django.urls import path

from . import views


urlpatterns = [
    path("reservations/", views.reservations, name="reservations"),
    path("reservations/<int:pk>/", views.reservation_detail, name="reservation-detail"),
    path("reservations/<int:pk>/confirmer/", views.confirmer_reservation, name="confirmer-reservation"),
    path("reservations/<int:pk>/annuler/", views.annuler_reservation, name="annuler-reservation"),
]
