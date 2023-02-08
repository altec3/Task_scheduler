import pytest
from django.urls import reverse
from rest_framework import status

from tests.utils import BaseTestCase
from goals.models import Board, BoardParticipant


@pytest.mark.django_db()
class TestCreateBoardView(BaseTestCase):
    """POST: Создание доски"""
    url = reverse('goals:board-create')

    def test_auth_required(self, client, faker):
        """Проверка permissions"""
        response = client.post(self.url, data=faker.pydict(1))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_failed_to_create_deleted_board(self, auth_client, faker):
        """POST: Невозможно создать доску со статусом 'is_deleted': True"""
        response = auth_client.post(self.url, data={
            'title': faker.sentence(),
            'is_deleted': True
        })
        assert response.status_code == status.HTTP_201_CREATED
        new_board = Board.objects.last()
        assert not new_board.is_deleted

    def test_creates_board_participant(self, auth_client, user, faker):
        """POST: Проверка создания владельца доски"""
        response = auth_client.post(self.url, data={
            'title': faker.sentence(),
        })
        assert response.status_code == status.HTTP_201_CREATED
        new_board = Board.objects.last()
        participants = new_board.participants.all()
        assert len(participants) == 1
        assert participants[0].user == user
        assert participants[0].role == BoardParticipant.Role.owner

    def test_success(self, auth_client, settings):
        """POST: Доска создана"""
        response = auth_client.post(self.url, data={
            'title': 'Board Title',
        })
        assert response.status_code == status.HTTP_201_CREATED
        new_board = Board.objects.last()
        assert response.json() == {
            'id': new_board.id,
            'created': self.datetime_to_str(new_board.created),
            'updated': self.datetime_to_str(new_board.updated),
            'title': 'Board Title',
            'is_deleted': False
        }
