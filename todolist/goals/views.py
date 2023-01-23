from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions

from goals.filters import GoalsFilter
from goals.models import Category, Goal, Comment
from goals.permissions import IsOwnerOrStaff
from goals.serializers import CategoryCreateSerializer, CategoryListSerializer, GoalCreateSerializer, \
    GoalListSerializer, CommentCreateSerializer, CommentListSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().select_related('user')
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title']

    _serializers = {
        'create': CategoryCreateSerializer,
    }
    _default_serializer = CategoryListSerializer

    _permissions = {
        'create': [permissions.IsAuthenticated()],
    }
    # TODO: Наличие класса IsOwnerOrStaff по вопросом. По факту отображение сущностей регулируется фильтром в queryset
    _default_permissions = [permissions.IsAuthenticated(), IsOwnerOrStaff()]

    def get_serializer_class(self):
        return self._serializers.get(self.action, self._default_serializer)

    def get_permissions(self):
        return self._permissions.get(self.action, self._default_permissions)

    # Переопределяем метод для отображения категорий с учетом полей author и is_deleted.
    def get_queryset(self):
        return super().get_queryset().filter(user_id=self.request.user.id, is_deleted=False)

    # Переопределяем метод для добавления в serializer поля с автором.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Переопределяем метод для исключения удаления категории из базы.
    def perform_destroy(self, instance: Category) -> Category:
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            instance.goals.update(status=Goal.Status.archived)
        return instance


class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all().select_related('user')
    # TODO: Наличие класса IsOwnerOrStaff по вопросом. По факту отображение сущностей регулируется фильтром в queryset
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    filterset_class = GoalsFilter
    ordering_fields = ['priority', 'due_date']
    ordering = ['priority']
    search_fields = ['title', 'description']

    _serializers = {
        'create': GoalCreateSerializer,
    }
    _default_serializer = GoalListSerializer

    def get_serializer_class(self):
        return self._serializers.get(self.action, self._default_serializer)

    # Переопределяем метод для отображения целей с учетом полей author и status.
    def get_queryset(self):
        return super().get_queryset().filter(
            user_id=self.request.user.id,
            status__lt=Goal.Status.archived,
            category__is_deleted=False,
        )

    # Переопределяем метод для добавления в serializer поля с автором.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Переопределяем метод для исключения удаления целей из базы.
    def perform_destroy(self, instance: Goal) -> Goal:
        with transaction.atomic():
            instance.status = Goal.Status.archived
            instance.save(update_fields=('status',))
        return instance


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().select_related('user', 'goal')
    # TODO: Наличие класса IsOwnerOrStaff по вопросом. По факту отображение сущностей регулируется фильтром в queryset
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['goal']
    ordering_fields = ['created']
    ordering = ['-created']

    _serializers = {
        'create': CommentCreateSerializer,
    }
    _default_serializer = CommentListSerializer

    def get_serializer_class(self):
        return self._serializers.get(self.action, self._default_serializer)

    # Переопределяем метод для отображения комментариев с учетом полей author и goal.
    def get_queryset(self):
        return super().get_queryset().filter(
            user_id=self.request.user.id,
            goal__status__lt=Goal.Status.archived,
        )

    # Переопределяем метод для добавления в serializer поля с автором.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
