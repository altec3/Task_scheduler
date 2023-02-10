import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import Category, Board, Goal, Comment
from tests.utils import BaseTestCase


@pytest.fixture()
def another_user(user_factory):
    return user_factory.create()


@pytest.mark.django_db()
class TestCommentList(BaseTestCase):
    url = reverse('goals:comment-list')

    @pytest.fixture(autouse=True)
    def setup(self, board_factory, category_factory, goal_factory, user):
        self.board: Board = board_factory.create(with_owner=user)
        self.category: Category = category_factory.create(board=self.board)
        self.goal: Goal = goal_factory.create(category=self.category)

    def test_auth_required(self, client):
        """Тест на endpoint GET: /goals/goal_comment/list

        Производит проверку требований аутентификации .
        """
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_not_board_participant(self,
                                        client, another_user, board_factory, category_factory,
                                        comment_factory, goal_factory
                                        ):
        """Тест на endpoint GET: /goals/goal_comment/list

        Производит проверку отображения комментариев, доступных пользователю.
        """
        comment: Comment = comment_factory.create(goal=self.goal)
        assert comment == self.goal.comments.last()
        assert self.board.participants.count() == 1

        another_board: Board = board_factory.create(with_owner=another_user)
        another_category: Category = category_factory.create(board=another_board)
        another_goal: Goal = goal_factory.create(category=another_category)
        another_comment: Comment = comment_factory.create(goal=another_goal)
        assert another_board.participants.count() == 1

        client.force_login(another_user)
        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                "id": another_comment.id,
                "user": {
                    "id": another_comment.user_id,
                    "username": another_comment.user.username,
                    "first_name": another_comment.user.first_name,
                    "last_name": another_comment.user.last_name,
                    "email": another_comment.user.email
                },
                "created": self.datetime_to_str(another_comment.created),
                "updated": self.datetime_to_str(another_comment.updated),
                "text": another_comment.text,
                "goal": another_goal.id
            },
        ]

    def test_sort_comments_by_created(self, auth_client, comment_factory):
        """Тест на endpoint GET: /goals/goal_comment/list

        Производит проверку функционирования сортировки комментариев по дате создания
        """
        created: list = [
            self.datetime_to_str(comment.created) for comment in comment_factory.create_batch(5, goal=self.goal)
        ]
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert [comment['created'] for comment in response.json()] == sorted(created, reverse=True)
