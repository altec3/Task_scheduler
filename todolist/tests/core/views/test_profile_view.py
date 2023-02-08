import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework import status

from tests.utils import BaseTestCase


@pytest.mark.django_db()
class TestProfileRetrieveView(BaseTestCase):
    """GET: Просмотр профиля пользователя"""
    url = reverse('core:user_retrieve')

    def test_auth_required(self, client):
        """Проверка permissions"""
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success(self, auth_client, user):
        """GET: Профиль пользователя предоставлен"""
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }


@pytest.mark.django_db()
class TestProfileUpdateView:
    """PUT, PATCH: Обновление профиля пользователя"""
    url = reverse('core:user_retrieve')

    def test_auth_required(self, client, faker):
        """Проверка permissions"""
        response = client.patch(self.url, data=faker.pydict(1))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('user__email', ['test_1@test.com'])
    def test_success(self, client, user):
        """PATCH: Профиль обновлен"""
        client.force_login(user)
        response = client.patch(self.url, data={'email': 'test_2@test.com'})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': 'test_2@test.com',
        }


@pytest.mark.django_db()
class TestDestroyProfileView:
    """DELETE:Выход пользователя из системы"""
    url = reverse('core:user_retrieve')

    def test_auth_required(self, client):
        """Проверка permissions"""
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_not_deleted(self, django_user_model, auth_client):
        """DELETE:Пользователь не удален из базы"""
        initial_count: int = django_user_model.objects.count()
        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert django_user_model.objects.count() == initial_count

    @pytest.mark.parametrize('backend', settings.AUTHENTICATION_BACKENDS)
    def test_cleanup_cookie(self, client, user, backend):
        """DELETE:Пользователь вышел из системы"""
        client.force_login(user=user, backend=backend)
        assert client.cookies['sessionid'].value
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not response.cookies['sessionid'].value
