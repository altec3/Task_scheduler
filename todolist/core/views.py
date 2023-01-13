from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from core.serializers import UserRegistrationSerializer


class UserCreateView(CreateAPIView):
    """Create a new user"""
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
