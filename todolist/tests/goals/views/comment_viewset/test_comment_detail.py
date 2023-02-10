import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import Category, Board, BoardParticipant, Goal, Comment
from tests.utils import BaseTestCase


@pytest.fixture()
def another_user(user_factory):
    return user_factory.create()


@pytest.mark.django_db()
class CommentTestCase(BaseTestCase):

    @pytest.fixture(autouse=True)
    def set_url(self, board_factory, category_factory, goal_factory, comment_factory, user):
        self.board: Board = board_factory.create(with_owner=user)
        self.category: Category = category_factory.create(board=self.board)
        self.goal: Goal = goal_factory.create(category=self.category)
        self.comment: Comment = comment_factory.create(goal=self.goal, user=user)
        self.url = reverse('goals:comment-detail', args=[self.comment.id])

    def test_auth_required(self, client):
        """Тест на endpoint [GET, PATCH, DELETE]: /goals/goal_comment/<id>

        Производит проверку требований аутентификации.
        """
        response = getattr(client, self.method)(self.url, {})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_not_board_participant(self, client, another_user):
        """Тест на endpoint [GET, PATCH, DELETE]: /goals/goal_comment/<id>

        Производит проверку отображения комментария к цели только в категории доски,
        в которой пользователь является участником
        """
        assert not self.board.participants.filter(user=another_user).count()

        client.force_login(another_user)
        response = getattr(client, self.method)(self.url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCommentRetrieve(CommentTestCase):
    method = 'get'

    def test_success(self, auth_client, user):
        """Тест на endpoint GET: /goals/goal_comment/<id>

        Производит проверку корректности структуры ответа при успешном запросе комментария.
        """
        assert self.comment.user == user

        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

        assert response.json() == {
            "id": self.comment.id,
            "user": {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            },
            "created": self.datetime_to_str(self.comment.created),
            "updated": self.datetime_to_str(self.comment.updated),
            "text": self.comment.text,
            "goal": self.goal.id
        }


class TestCommentUpdate(CommentTestCase):
    method = 'patch'

    def test_failed_update_comment_by_non_owner(self, client, user, another_user, faker):
        """Тест на endpoint PATCH: /goals/goal_comment/<id>

        Производит проверку отсутствия у пользователя возможности редактировать комментарий,
        если он не является его автором
        """
        assert self.comment.user == user

        client.force_login(another_user)
        response = client.patch(self.url, {'text': faker.text()})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_success_update_comment_by_owner(self, faker, auth_client):
        """Тест на endpoint PATCH: /goals/goal_comment/<id>

        Производит проверку наличия у пользователя возможности редактировать комментарий,
        если он является его автором
        """
        new_text = faker.text()

        response = auth_client.patch(self.url, {'text': new_text})
        assert response.status_code == status.HTTP_200_OK

        self.comment.refresh_from_db(fields=('text',))
        assert self.comment.text == new_text


class TestCommentDestroy(CommentTestCase):
    method = 'delete'

    def test_failed_delete_comment_by_non_owner(self, client, user, another_user):
        """Тест на endpoint DELETE: /goals/goal_comment/<id>

        Производит проверку отсутствия у пользователя возможности удалить комментарий,
        если он не является его автором.
        """
        assert self.comment.user == user

        client.force_login(another_user)
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_success_delete_comment_by_owner(self, auth_client):
        """Тест на endpoint DELETE: /goals/goal_comment/<id>

        Производит проверку наличия у пользователя возможности удалить комментарий,
        если он является его автором.
        """
        assert len(Comment.objects.all()) == 1

        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Comment.objects.all()
