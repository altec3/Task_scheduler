from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.models import User
from core.serializers import UserRegistrationSerializer, UserLoginSerializer, ProfileSerializer


class UserCreateView(CreateAPIView):
    """Create a new user"""
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer


class UserLoginView(CreateAPIView):
    """Login a user"""
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        login(request=self.request, user=serializer.save())


class UserRetrieveView(RetrieveUpdateDestroyAPIView):
    """Retrieve a user"""
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        logout(self.request)
