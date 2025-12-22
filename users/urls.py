from django.urls import path
from users.views import LoginAPIView, RegisterAPIView

urlpatterns = [
    path("auth/login/", LoginAPIView.as_view(), name="login"),
    path("auth/register/", RegisterAPIView.as_view(), name="register"),
]
