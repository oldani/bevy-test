from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .serializers import ProfileSerializer, NotificationSerializer


class ProfileView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class NotificationsView(ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).all()