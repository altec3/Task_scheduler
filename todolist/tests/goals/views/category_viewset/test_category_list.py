import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import Category, Board
from tests.utils import BaseTestCase


@pytest.fixture()
def another_user(user_factory):
    return user_factory.create()


@pytest.mark.django_db()
class TestCategoryList(BaseTestCase):
    url = reverse('goals:category-list')

    @pytest.fixture(autouse=True)
    def setup(self, board_factory, user):
        self.board: Board = board_factory.create(with_owner=user)

    def test_auth_required(self, client):
        """Тест на endpoint GET: /goals/goal_category/list

        Производит проверку требований аутентификации .
        """
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_not_board_participant(self, client, another_user, board_factory, category_factory):
        """Тест на endpoint GET: /goals/goal_category/list

        Производит проверку отображения категорий, доступных пользователю.
        """
        cat: Category = category_factory.create(board=self.board)
        assert cat.board.participants.count() == 1

        another_board = board_factory.create(with_owner=another_user)
        another_cat = category_factory.create(board=another_board, user=another_user)
        assert another_board.participants.count() == 1

        client.force_login(another_user)
        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                "id": another_cat.id,
                "user": {
                    "id": another_user.id,
                    "username": another_user.username,
                    "first_name": another_user.first_name,
                    "last_name": another_user.last_name,
                    "email": another_user.email
                },
                "created": self.datetime_to_str(another_cat.created),
                "updated": self.datetime_to_str(another_cat.updated),
                "title": another_cat.title,
                "is_deleted": False,
                "board": another_board.id
            },
        ]

    def test_sort_category_by_title(self, auth_client, category_factory):
        """Тест на endpoint GET: /goals/goal_category/list

        Производит проверку функционирования сортировки категорий по названию
        """
        for title in ['cat2', 'cat1', 'cat4', 'cat3']:
            category_factory.create(title=title, board=self.board)

        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert [category['title'] for category in response.json()] == ['cat1', 'cat2', 'cat3', 'cat4']

    def test_category_pagination(self, auth_client, category_factory):
        """Тест на endpoint GET: /goals/goal_category/list

        Производит проверку функционирования пагинации
        """
        category_factory.create_batch(size=10, board=self.board)

        limit_response = auth_client.get(self.url, {'limit': 3})
        assert limit_response.status_code == status.HTTP_200_OK
        assert limit_response.json()['count'] == 10
        assert len(limit_response.json()['results']) == 3

        offset_response = auth_client.get(self.url, {'limit': 100, 'offset': 8})
        assert offset_response.status_code == status.HTTP_200_OK
        assert offset_response.json()['count'] == 10
        assert len(offset_response.json()['results']) == 2
