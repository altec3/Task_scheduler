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
        """Проверка permissions IsAuthenticated"""
        response = getattr(client, self.method)(self.url, {})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_not_board_participant(self, client, another_user):
        """Проверка permissions BoardPermissions"""
        assert not self.board.participants.filter(user=another_user).count()

        client.force_login(another_user)
        response = getattr(client, self.method)(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestRetrieveBoardView(BoardTestCase):
    """GET: Просмотр информации о доске"""
    method = 'get'

    def test_success(self, auth_client, user):
        """GET: Проверка - успешный запрос"""
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


class TestDestroyBoardView(BoardTestCase):
    """DELETE: Удаление доски"""
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
    def test_only_owner_have_to_delete_board(self, auth_client, user_role):
        """DELETE: Проверка - только автор может удалить доску"""
        self.participant.role = user_role
        self.participant.save(update_fields=('role',))

        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success(self, auth_client):
        """
        DELETE: Проверка - успешный запрос:
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


class TestUpdateBoardView(BoardTestCase):
    """PATCH: Редактирование доски"""
    method = 'patch'

    @pytest.fixture(autouse=True)
    def setup(self):  # noqa: PT004
        self.participant: BoardParticipant = self.board.participants.last()

    @pytest.mark.parametrize(
        'user_role',
        [BoardParticipant.Role.writer, BoardParticipant.Role.reader],
        ids=['writer', 'reader']
    )
    def test_reader_or_writer_failed_to_update_board(self, faker, user_role, auth_client):
        """PATCH: Проверка - только автор может редактировать доску"""
        self.participant.role = user_role
        self.participant.save(update_fields=('role',))

        response = auth_client.patch(self.url, faker.pydict(1))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_title_by_owner(self, auth_client, faker):
        """PATCH: Проверка - успешный запрос на изменение названия доски"""
        assert self.participant.role == BoardParticipant.Role.owner
        new_title = faker.sentence()

        response = auth_client.patch(self.url, {'title': new_title})
        assert response.status_code == status.HTTP_200_OK

        self.board.refresh_from_db(fields=('title',))
        assert self.board.title == new_title
