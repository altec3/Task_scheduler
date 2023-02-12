import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import Category, Board, BoardParticipant, Goal
from tests.utils import BaseTestCase


@pytest.fixture()
def another_user(user_factory):
    return user_factory.create()


@pytest.mark.django_db()
class GoalTestCase(BaseTestCase):

    @pytest.fixture(autouse=True)
    def set_url(self, board_factory, category_factory, goal_factory, user):
        self.board: Board = board_factory.create(with_owner=user)
        self.category: Category = category_factory.create(board=self.board)
        self.goal: Goal = goal_factory.create(category=self.category)
        self.url = reverse('goals:goal-detail', args=[self.goal.id])

    def test_auth_required(self, client):
        """Тест на endpoint [GET, PATCH, DELETE]: /goals/goal/<id>

        Производит проверку требований аутентификации.
        """
        response = getattr(client, self.method)(self.url, {})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_not_board_participant(self, client, another_user):
        """Тест на endpoint [GET, PATCH, DELETE]: /goals/goal/<id>

        Производит проверку отображения цели только категории доски,
        в которой пользователь является участником
        """
        assert not self.board.participants.filter(user=another_user).count()

        client.force_login(another_user)
        response = getattr(client, self.method)(self.url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGoalRetrieve(GoalTestCase):
    method = 'get'

    def test_success(self, auth_client, user):
        """Тест на endpoint GET: /goals/goal/<id>

        Производит проверку корректности структуры ответа при успешном запросе цели.
        """
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

        assert self.board.participants.count() == 1
        participant: BoardParticipant = self.board.participants.last()
        assert participant.user == user

        assert response.json() == {
            "id": self.goal.id,
            "user": {
                "id": self.goal.user.id,
                "username": self.goal.user.username,
                "first_name": self.goal.user.first_name,
                "last_name": self.goal.user.last_name,
                "email": self.goal.user.email
            },
            "created": self.datetime_to_str(self.goal.created),
            "updated": self.datetime_to_str(self.goal.updated),
            "title": self.goal.title,
            "description": self.goal.description,
            "status": 1,
            "priority": 2,
            "due_date": None,
            "category": self.category.id
        }


class TestGoalUpdate(GoalTestCase):
    method = 'patch'

    @pytest.fixture(autouse=True)
    def setup(self):
        self.participant: BoardParticipant = self.category.board.participants.last()

    def test_failed_update_goal_by_reader(self, faker, auth_client):
        """Тест на endpoint PATCH: /goals/goal/<id>

        Производит проверку отсутствия у пользователя возможности редактировать цель в категории доски,
        где он является читателем.
        """
        self.participant.role = BoardParticipant.Role.reader
        self.participant.save(update_fields=('role',))
        assert self.participant.role == BoardParticipant.Role.reader

        response = auth_client.patch(self.url, data={
            'title': faker.sentence(),
            'category': self.category.id
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        'user_role',
        [BoardParticipant.Role.owner, BoardParticipant.Role.writer],
        ids=['owner', 'writer']
    )
    def test_success_update_goal_by_owner_or_writer(self, auth_client, faker, user_role):
        """Тест на endpoint PATCH: /goals/goal/<id>

        Производит проверку наличия у пользователя возможности редактировать цель в категории доски,
        где он является автором или редактором.
        """
        self.participant.role = user_role
        self.participant.save(update_fields=('role',))
        assert self.participant.role == user_role

        new_title = faker.sentence()

        response = auth_client.patch(self.url, {'title': new_title})
        assert response.status_code == status.HTTP_200_OK

        self.goal.refresh_from_db(fields=('title',))
        assert self.goal.title == new_title


class TestGoalDestroy(GoalTestCase):
    method = 'delete'

    @pytest.fixture(autouse=True)
    def setup(self):
        self.participant: BoardParticipant = self.board.participants.last()

    def test_failed_delete_goal_by_reader(self, auth_client):
        """Тест на endpoint DELETE: /goals/goal/<id>

        Производит проверку отсутствия у пользователя возможности удалить цель в категории доски,
        где он является читателем.
        """
        self.participant.role = BoardParticipant.Role.reader
        self.participant.save(update_fields=('role',))
        assert self.participant.role == BoardParticipant.Role.reader

        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        'user_role',
        [BoardParticipant.Role.owner, BoardParticipant.Role.writer],
        ids=['owner', 'writer']
    )
    def test_success_delete_goal_by_owner_or_writer(self, auth_client, user_role):
        """Тест на endpoint DELETE: /goals/goal/<id>

        Производит проверку наличия у пользователя возможности удалить цель в категории доски,
        где он является автором или редактором. А так же выполнение следующего условия:
            - цель: Status == archived
        """
        self.participant.role = user_role
        self.participant.save(update_fields=('role',))
        assert self.participant.role == user_role

        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        self.goal.refresh_from_db(fields=('status',))
        assert self.goal.status == Goal.Status.archived
