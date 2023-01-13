import django.contrib.auth.password_validation as validators
from django.core import exceptions
from rest_framework import serializers

from core.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True)
    password_repeat = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')

    def is_valid(self, *, raise_exception=False):

        # Проверка соответствия полей password и password_repeat
        password_repeat = self.initial_data.pop('password_repeat')
        if self.initial_data['password'] != password_repeat:
            raise serializers.ValidationError(
                "The two password fields didn't match.")

        # Проверка надежности пароля
        user = User(**self.initial_data)
        errors = dict()
        try:
            validators.validate_password(password=password_repeat, user=user)
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return super().is_valid(raise_exception=raise_exception)

    def create(self, validated_data):
        user = super().create(validated_data)

        user.set_password(user.password)
        user.save()

        return user
