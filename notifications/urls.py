from django.urls import path
from .views import ProfileView


urlpatterns = [
    path(
        "preferences/", ProfileView.as_view(), name="notification-preferences"
    ),
]
