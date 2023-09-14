from django.urls import path

from . import views

urlpatterns = [
        path('signup/', views.signup, name='signup'),
        path('login/', views.auth_login_form, name='login'),
        path('login_action/', views.auth_login, name='login_action'),
        path('logout/', views.auth_logout, name='logout'),
        path('auth_bar', views.auth_bar, name='auth_bar'),
        path('debug', views.debug, name='debug'),
        ]
