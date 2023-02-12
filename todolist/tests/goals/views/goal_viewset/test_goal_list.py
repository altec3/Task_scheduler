import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import Category, Board, Goal
from tests.utils import BaseTestCase


@pytest.fixture()
def another_user(user_factory):
    return user_factory.create()


@pytest.mark.django_db()
class TestGoalList(BaseTestCase):
    url = reverse('goals:goal-list')

    @pytest.fixture(autouse=True)
    def setup(self, board_factory, category_factory, user):
        self.board: Board = board_factory.create(with_owner=user)
        self.category: Category = category_factory.create(board=self.board)

    def test_auth_required(self, client):
        """Тест на endpoint GET: /goals/goal/list

        Производит проверку требований аутентификации .
        """
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_not_board_participant(self, client, another_user, board_factory, category_factory, goal_factory):
        """Тест на endpoint GET: /goals/goal/list

        Производит проверку отображения целей, доступных пользователю.
        """
        goal: Goal = goal_factory.create(category=self.category)
        assert goal.category.board.participants.count() == 1

        another_board: Board = board_factory.create(with_owner=another_user)
        another_category: Category = category_factory.create(board=another_board)
        another_goal: Goal = goal_factory.create(category=another_category)
        assert another_goal.category.board.participants.count() == 1

        client.force_login(another_user)
        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                "id": another_goal.id,
                "user": {
                    "id": another_goal.user.id,
                    "username": another_goal.user.username,
                    "first_name": another_goal.user.first_name,
                    "last_name": another_goal.user.last_name,
                    "email": another_goal.user.email
                },
                "created": self.datetime_to_str(another_goal.created),
                "updated": self.datetime_to_str(another_goal.updated),
                "title": another_goal.title,
                "description": another_goal.description,
                "status": another_goal.status,
                "priority": another_goal.priority,
                "due_date": another_goal.due_date,
                "category": another_goal.category_id
            },
        ]

    def test_sort_goals_by_priority(self, auth_client, goal_factory):
        """Тест на endpoint GET: /goals/goal/list

        Производит проверку функционирования сортировки целей по приоритету
        """
        for priority in [2, 1, 4, 3]:
            goal_factory.create(priority=priority, category=self.category)

        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert [goal['priority'] for goal in response.json()] == [1, 2, 3, 4]
