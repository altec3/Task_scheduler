import pytest
from factory.django import DjangoModelFactory
from rest_framework import status
from rest_framework.reverse import reverse

from tests.factories import (
    BoardFactory as board_factory,
    CategoryFactory as category_factory,
    GoalFactory as goal_factory,
    CommentFactory as comment_factory
)


@pytest.mark.django_db()
@pytest.mark.parametrize(
    'factory, url', [
        (board_factory, reverse('goals:board-list')),
        (category_factory, reverse('goals:category-list')),
        (comment_factory, reverse('goals:comment-list'))
    ],
    ids=['board-list', 'category-list', 'comment-list']
)
def test_pagination(factory: DjangoModelFactory, url: str, auth_client, user):
    """Тест на эндпоинты GET: {basename}-list

    Производит проверку функционирования пагинации
    """
    if factory == board_factory:
        factory.create_batch(size=10, with_owner=user)

    elif factory == category_factory:
        board = board_factory.create(with_owner=user)
        factory.create_batch(size=10, board=board)

    elif factory == comment_factory:
        board = board_factory.create(with_owner=user)
        category = category_factory.create(board=board)
        goal = goal_factory.create(category=category)
        factory.create_batch(size=10, goal=goal, user=user)


    limit_response = auth_client.get(url, {'limit': 3})
    assert limit_response.status_code == status.HTTP_200_OK
    assert limit_response.json()['count'] == 10
    assert len(limit_response.json()['results']) == 3

    offset_response = auth_client.get(url, {'limit': 100, 'offset': 8})
    assert offset_response.status_code == status.HTTP_200_OK
    assert offset_response.json()['count'] == 10
    assert len(offset_response.json()['results']) == 2
