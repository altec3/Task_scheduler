import pytest
from django.urls import reverse
from rest_framework import status

from tests.utils import BaseTestCase


@pytest.mark.django_db()
class TestBoardList(BaseTestCase):
    url = reverse('goals:board-list')

    def test_auth_required(self, client):
        """Тест на эндпоинт GET: /goals/bord/list

        Производит проверку требований аутентификации .
        """
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_not_board_participant(self, auth_client, board, user, board_factory):
        """Тест на эндпоинт GET: /goals/board/list

        Производит проверку отображения досок, доступных пользователю.
        """
        assert not board.participants.count()
        another_board = board_factory.create(with_owner=user)
        assert another_board.participants.count() == 1

        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                'id': another_board.id,
                'created': self.datetime_to_str(another_board.created),
                'updated': self.datetime_to_str(another_board.updated),
                'title': another_board.title,
                'is_deleted': False
            }
        ]

    def test_sort_boards_by_title(self, auth_client, board_factory, user):
        """Тест на эндпоинт GET: /goals/board/list

        Производит проверку функционирования сортировки досок по названию
        """
        for title in ['t2', 't1', 't4', 't3']:
            board_factory.create(title=title, with_owner=user)

        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert [board['title'] for board in response.json()] == ['t1', 't2', 't3', 't4']
