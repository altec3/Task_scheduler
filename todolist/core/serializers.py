from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from core.forms import PasswordField
from core.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = PasswordField(required=True)
    password_repeat = PasswordField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')

    def validate(self, attrs):
        # Проверка соответствия полей password и password_repeat
        if attrs['password'] != attrs['password_repeat']:
            raise serializers.ValidationError(
                "The two password fields didn't match.")

        return attrs

    def create(self, validated_data):
        del validated_data['password_repeat']
        user = super().create(validated_data)

        user.set_password(user.password)
        user.save()

        return user


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = PasswordField(required=True)

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "password")
        read_only_fields = ("id", "username", "first_name", "last_name", "email")

    def create(self, validated_data: dict) -> User:
        if not (
            user := authenticate(
                username=validated_data["username"],
                password=validated_data["password"]
            )
        ):
            raise AuthenticationFailed
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email")
