import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import BoardParticipant, Category, Goal
from tests.utils import BaseTestCase


@pytest.fixture()
def another_user(user_factory):
    return user_factory.create()


@pytest.mark.django_db()
class BoardTestCase(BaseTestCase):

    @pytest.fixture(autouse=True)
    def set_url(self, board_factory, user):  # noqa: PT004
        self.board = board_factory.create(with_owner=user)
        self.url = reverse('goals:board-detail', args=[self.board.id])

    def test_auth_required(self, client):
        """Тест на эндпоинт [GET, PATCH, DELETE]: /goals/board/<id>

        Производит проверку требований аутентификации.
        """
        response = getattr(client, self.method)(self.url, {})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_not_board_participant(self, client, another_user):
        """Тест на эндпоинт [GET, PATCH, DELETE]: /goals/board/<id>

        Производит проверку отображения только той доски,
        в которой пользователь является участником
        """
        assert not self.board.participants.filter(user=another_user).count()

        client.force_login(another_user)
        response = getattr(client, self.method)(self.url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestBoardRetrieve(BoardTestCase):
    method = 'get'

    def test_success(self, auth_client, user):
        """Тест на эндпоинт GET: /goals/board/<id>

        Производит проверку корректности структуры ответа при успешном запросе доски.
        """
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

        assert self.board.participants.count() == 1
        participant: BoardParticipant = self.board.participants.last()
        assert participant.user == user

        assert response.json() == {  # noqa: ECE001
            'id': self.board.id,
            'participants': [
                {
                    'id': participant.id,
                    'role': BoardParticipant.Role.owner.value,
                    'user': user.username,
                    'created': self.datetime_to_str(participant.created),
                    'updated': self.datetime_to_str(participant.created),
                    'board': participant.board_id
                }
            ],
            'created': self.datetime_to_str(self.board.created),
            'updated': self.datetime_to_str(self.board.updated),
            'title': self.board.title,
            'is_deleted': False
        }


class TestBoardUpdate(BoardTestCase):
    method = 'patch'

    @pytest.fixture(autouse=True)
    def setup(self):  # noqa: PT004
        self.participant: BoardParticipant = self.board.participants.last()

    @pytest.mark.parametrize(
        'user_role',
        [BoardParticipant.Role.writer, BoardParticipant.Role.reader],
        ids=['writer', 'reader']
    )
    def test_failed_update_board_by_reader_or_writer(self, faker, user_role, auth_client):
        """Тест на эндпоинт PATCH: /goals/board/<id>

        Производит проверку отсутствия у пользователя возможности редактировать доску,
        в которой он является редактором или читателем.
        """
        self.participant.role = user_role
        self.participant.save(update_fields=('role',))
        assert self.participant.role == user_role

        response = auth_client.patch(self.url, faker.pydict(1))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success_update_board_by_owner(self, auth_client, faker):
        """Тест на эндпоинт PATCH: /goals/board/<id>

        Производит проверку наличия у пользователя возможности редактировать доску,
        в которой он является автором.
        """
        assert self.participant.role == BoardParticipant.Role.owner
        new_title = faker.sentence()

        response = auth_client.patch(self.url, {'title': new_title})
        assert response.status_code == status.HTTP_200_OK

        self.board.refresh_from_db(fields=('title',))
        assert self.board.title == new_title


class TestBoardDestroy(BoardTestCase):
    method = 'delete'

    @pytest.fixture(autouse=True)
    def setup(self, category_factory, goal_factory, user):  # noqa: PT004
        self.cat: Category = category_factory.create(board=self.board, user=user)
        self.goal: Goal = goal_factory.create(category=self.cat, user=user)
        self.participant: BoardParticipant = self.board.participants.last()

    @pytest.mark.parametrize(
        'user_role',
        [BoardParticipant.Role.writer, BoardParticipant.Role.reader],
        ids=['writer', 'reader']
    )
    def test_failed_delete_board_by_reader_or_writer(self, auth_client, user_role):
        """Тест на эндпоинт DELETE: /goals/board/<id>

        Производит проверку отсутствия у пользователя возможности удалить доску,
        в которой он является редактором или читателем.
        """
        self.participant.role = user_role
        self.participant.save(update_fields=('role',))

        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success_delete_board_by_owner(self, auth_client):
        """Тест на эндпоинт DELETE: /goals/board/<id>

        Производит проверку наличия у пользователя возможности удалить доску,
        в которой он является автором. А так же выполнение следующих условий:
            - доска: is_deleted == True
            - категория: is_deleted == True
            - цель: Status == archived
        """
        assert self.participant.role == BoardParticipant.Role.owner

        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        self.board.refresh_from_db(fields=('is_deleted',))
        self.cat.refresh_from_db(fields=('is_deleted',))
        self.goal.refresh_from_db(fields=('status',))
        assert self.board.is_deleted
        assert self.cat.is_deleted
        assert self.goal.status == Goal.Status.archived
