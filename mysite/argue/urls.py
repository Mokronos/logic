from django.urls import path

from . import views

urlpatterns = [
        path("", views.index, name="index"),
        path("clicked", views.clicked, name="clicked"),
        path("account/edit", views.account_edit, name="account_edit"),
        ]
