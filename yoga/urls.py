from django.urls import path
from .views import *

urlpatterns = [
    path("", home),
    path("accounts/login/", login, name="login"),
    path("accounts/logout/", logout, name="logout"),
    path("accounts/register/", register, name="register"),
    path("payment/", payment, name="payment"),
    path("payment/otp/", otp, name="otp"),
]
