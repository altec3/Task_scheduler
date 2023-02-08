import pytest
from django.urls import reverse
from rest_framework import status

from tests.utils import BaseTestCase


@pytest.mark.django_db()
class TestLoginView(BaseTestCase):
    url = reverse('core:user_login')

    def test_invalid_credentials(self, client, user_factory):
        """Предоставлены не верные логин и пароль"""

        user = user_factory.build()
        response = client.post(self.url, data={
            'username': user.username,
            'password': user.password,
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_password(self, client, user_factory, faker):
        """Предоставлен не верный пароль"""

        user = user_factory.create()
        password = faker.password()
        response = client.post(self.url, data={
            'username': user.username,
            'password': password,
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success(self, client, faker, user_factory):
        """Предоставлены верные логин и пароль"""

        password = faker.password()
        user = user_factory.create(password=password)
        response = client.post(self.url, data={
            'username': user.username,
            'password': password,
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username
        }
