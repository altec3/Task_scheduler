import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import Category, Board, BoardParticipant
from tests.utils import BaseTestCase


@pytest.mark.django_db()
class TestCategoryCreate(BaseTestCase):
    url = reverse('goals:category-create')

    @pytest.fixture(autouse=True)
    def setup(self, board_factory, user):
        self.board: Board = board_factory.create(with_owner=user)
        self.participant: BoardParticipant = self.board.participants.last()

    def test_auth_required(self, client):
        """Тест на endpoint POST: /goals/goal_category/create

        Производит проверку требований аутентификации .
        """
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_failed_to_create_deleted_category(self, auth_client, faker):
        """Тест на endpoint POST: /goals/goal_category/create

        Производит проверку отсутствия возможности создать категорию со статусом 'is_deleted': True
        """
        response = auth_client.post(self.url, data={
            'title': faker.sentence(),
            'board': self.board.id,
            'is_deleted': True
        })
        assert response.status_code == status.HTTP_201_CREATED
        new_category: Category = Category.objects.last()
        assert not new_category.is_deleted

    def test_failed_create_category_by_reader(self, auth_client, faker):
        """Тест на endpoint POST: /goals/goal_category/create

        Производит проверку отсутствия возможности у пользователя создать категорию в доске,
        где он является читателем.
        """
        self.participant.role = BoardParticipant.Role.reader
        self.participant.save(update_fields=('role',))
        assert self.participant.role == BoardParticipant.Role.reader

        response = auth_client.post(self.url, data={
            'title': faker.sentence(),
            'board': self.board.id
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        'user_role',
        [BoardParticipant.Role.owner, BoardParticipant.Role.writer],
        ids=['owner', 'writer']
    )
    def test_success_create_category_by_owner_or_writer(self, auth_client, user_role, faker):
        """Тест на endpoint POST: /goals/goal_category/create

        Производит проверку наличия возможности у пользователя создать категорию в доске,
        где он является автором или писателем.
        """
        self.participant.role = user_role
        self.participant.save(update_fields=('role',))

        response = auth_client.post(self.url, data={
            'title': faker.sentence(),
            'board': self.board.id
        })
        assert response.status_code == status.HTTP_201_CREATED
