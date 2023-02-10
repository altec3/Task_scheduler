import pytest
from django.urls import reverse
from rest_framework import status

from tests.utils import BaseTestCase


@pytest.mark.django_db()
class TestUserCreateView(BaseTestCase):
    url = reverse('core:user_create')

    def test_passwords_missmatch(self, client, faker):
        """Тест на эндпоинт POST: /core/signup

        Производит проверку соответствия полей 'Password' и 'Password repeat'.
        """
        response = client.post(self.url, data={
            'username': faker.user_name(),
            'password': faker.password(),
            'password_repeat': faker.password(),
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'password_repeat': ['The two password fields didn\'t match.']}

    def test_invalid_password(self, client, faker, invalid_password):
        """Тест на эндпоинт POST: /core/signup

        Производит проверку процедуры валидации пароля.
        Проверяется проверка пароля на соответствие следующим требованиям:
            - пароль имеет соответствующую длину
            - пароль не входит в список часто встречающихся паролей
            - пароль не состоит только из чисел
        """
        response = client.post(self.url, data={
            'username': faker.user_name(),
            'password': invalid_password,
            'password_repeat': invalid_password,
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_success(self, client, user_factory, django_user_model):
        """Тест на эндпоинт POST: /core/signup

        Производит проверку процедуры успешной регистрации пользователя,
        а также проверку корректности структуры ответа.
        """
        assert not django_user_model.objects.count()

        user_data = user_factory.build()
        response = client.post(self.url, data={
            'username': user_data.username,
            'password': user_data.password,
            'password_repeat': user_data.password,
        })
        assert response.status_code == status.HTTP_201_CREATED

        assert django_user_model.objects.count() == 1
        new_user = django_user_model.objects.last()
        assert response.json() == {
            'id': new_user.id,
            'username': user_data.username,
            'first_name': '',
            'last_name': '',
            'email': ''
        }
        assert new_user.password != user_data.password
        assert new_user.check_password(user_data.password)
