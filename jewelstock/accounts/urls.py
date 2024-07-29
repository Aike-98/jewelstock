from django.urls import path
from . import views

urlpatterns = [ 
    path("accounts/signup/", views.signup, name="signup"),

    path("accounts/login/", views.login, name="login"),
    path("accounts/logout/", views.logout, name="logout"),
    path("accounts/password_change/", views.password_change, name="password_change"),
    path("accounts/password_change/done/", views.password_change_done, name="password_change_done"),
    path("accounts/password_reset/", views.password_reset, name="password_reset"),
    path("accounts/password_reset/done/", views.password_reset_done, name="password_reset_done"),
    path("accounts/reset/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
    path("accounts/reset/done/", views.password_reset_complete, name="password_reset_complete"),
]
