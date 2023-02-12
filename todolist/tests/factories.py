import factory
from django.utils import timezone
from pytest_factoryboy import register

from goals.models import BoardParticipant


@register
class UserFactory(factory.django.DjangoModelFactory):
    """Фабрика по созданию экземпляра модели User"""

    username = factory.Faker('user_name')
    password = factory.Faker('password')
    email = ''

    class Meta:
        model = 'core.User'

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._get_manager(model_class).create_user(*args, **kwargs)


class DatesFactoryMixin(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    created = factory.LazyFunction(timezone.now)
    updated = factory.LazyFunction(timezone.now)


@register
class BoardFactory(DatesFactoryMixin):
    """Фабрика по созданию экземпляра модели Board"""

    title = factory.Faker('sentence')

    class Meta:
        model = 'goals.Board'

    @factory.post_generation
    def with_owner(self, create, owner, **kwargs):
        if owner:
            BoardParticipant.objects.create(board=self, user=owner, role=BoardParticipant.Role.owner)


@register
class BoardParticipantFactory(DatesFactoryMixin):
    """Фабрика по созданию экземпляра модели BoardParticipant"""
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = 'goals.BoardParticipant'


@register
class CategoryFactory(DatesFactoryMixin):
    """Фабрика по созданию экземпляра модели Category"""

    board = factory.SubFactory(BoardFactory)
    title = factory.Faker('sentence')
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = 'goals.Category'


@register
class GoalFactory(DatesFactoryMixin):
    """Фабрика по созданию экземпляра модели Goal"""

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    title = factory.Faker('sentence')

    class Meta:
        model = 'goals.Goal'


@register
class CommentFactory(DatesFactoryMixin):
    """Фабрика по созданию экземпляра модели Comment"""

    user = factory.SubFactory(UserFactory)
    goal = factory.SubFactory(GoalFactory)
    text = factory.Faker('text')

    class Meta:
        model = 'goals.Comment'
