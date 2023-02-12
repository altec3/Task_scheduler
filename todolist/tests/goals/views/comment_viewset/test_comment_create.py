import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import Category, Board, BoardParticipant, Goal
from tests.utils import BaseTestCase


@pytest.mark.django_db()
class TestCommentCreate(BaseTestCase):
    url = reverse('goals:comment-create')

    @pytest.fixture(autouse=True)
    def setup(self, board_factory, category_factory, goal_factory, user):
        self.board: Board = board_factory.create(with_owner=user)
        self.category: Category = category_factory.create(board=self.board)
        self.goal: Goal = goal_factory.create(category=self.category)
        self.participant: BoardParticipant = self.board.participants.last()

    def test_auth_required(self, client):
        """Тест на endpoint POST: /goals/goal_comment/create

        Производит проверку требований аутентификации .
        """
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_failed_create_comment_by_reader(self, auth_client, faker):
        """Тест на endpoint POST: /goals/goal_comment/create

        Производит проверку отсутствия возможности у пользователя создать комментарий к цели
        в категории доски, где он является читателем.
        """
        self.participant.role = BoardParticipant.Role.reader
        self.participant.save(update_fields=('role',))
        assert self.participant.role == BoardParticipant.Role.reader

        response = auth_client.post(self.url, data={
            'text': faker.text(),
            'goal': self.goal.id
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        'user_role',
        [BoardParticipant.Role.owner, BoardParticipant.Role.writer],
        ids=['owner', 'writer']
    )
    def test_success_create_comment_by_owner_or_writer(self, auth_client, user_role, faker):
        """Тест на endpoint POST: /goals/goal_comment/create

        Производит проверку наличия возможности у пользователя создать комментарий к цели
        в категории доски, где он является автором или писателем.
        """
        self.participant.role = user_role
        self.participant.save(update_fields=('role',))
        assert self.participant.role == user_role

        response = auth_client.post(self.url, data={
            'text': faker.text(),
            'goal': self.goal.id
        })
        assert response.status_code == status.HTTP_201_CREATED
