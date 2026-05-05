from django.urls import path

from . import views


urlpatterns = [
    path("utilisateurs/", views.utilisateurs, name="utilisateurs"),
    path("utilisateurs/<int:pk>/", views.utilisateur_detail, name="utilisateur-detail"),
]
