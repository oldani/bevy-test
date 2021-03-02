from django.urls import path
from .views import ProfileView, NotificationsView


urlpatterns = [
    path(
        "preferences/", ProfileView.as_view(), name="notification-preferences"
    ),
    path("", NotificationsView.as_view(), name="notifications"),
]
