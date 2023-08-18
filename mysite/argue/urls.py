from django.urls import path

from . import views

urlpatterns = [
        path("", views.index, name="index"),
        path("clicked", views.clicked, name="clicked"),
        path("edit", views.edit, name="edit"),
        ]
