from django.contrib.auth import authenticate, hashers
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, ValidationError

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

    def create(self, validated_data: dict) -> User:
        del validated_data['password_repeat']
        validated_data['password'] = hashers.make_password(validated_data['password'])

        return super().create(validated_data)


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


class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, style={'input_type': 'password'}, write_only=True)
    new_password = PasswordField(required=True)

    def validate_old_password(self, value: str) -> str:
        if not self.instance.check_password(value):
            raise ValidationError('Old password is incorrect')

        return value

    def update(self, instance: User, validated_data: dict) -> User:
        instance.set_password(validated_data['new_password'])
        instance.save(update_fields=('password', ))
        return instance

    def create(self, validated_data):
        raise NotImplementedError
