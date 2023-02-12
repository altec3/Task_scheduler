from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.models import User
from core.serializers import UserRegistrationSerializer, UserLoginSerializer, ProfileSerializer, \
    UpdatePasswordSerializer


class UserCreateView(CreateAPIView):
    """Представление для обработки запроса на эндпоинт POST: /core/signup

    Регистрация пользователя
    """
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer


class UserLoginView(CreateAPIView):
    """Представление для обработки запроса на эндпоинт POST: /core/login

    Авторизация пользователя
    """
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    #: Реализация авторизации пользователя
    def perform_create(self, serializer):
        login(request=self.request, user=serializer.save())


class UserRetrieveView(RetrieveUpdateDestroyAPIView):
    """Представление для обработки запроса на эндпоинт [GET, PUT, PATCH, DELETE]: /core/profile

    Редактирование профиля пользователя
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

    #: Выход из текущего аккаунта (logout)
    def perform_destroy(self, instance):
        logout(self.request)


class UpdatePasswordView(UpdateAPIView):
    """Представление для обработки запроса на эндпоинт [PUT, PATCH]: /core/update_password

    Изменение пароля пользователя
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UpdatePasswordSerializer

    def get_object(self):
        return self.request.user
