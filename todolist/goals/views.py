from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions

from goals.filters import GoalsFilter
from goals.models import Category, Goal, Comment, Board
from goals.permissions import BoardPermissions, IsOwnerOrWriter
from goals.serializers import (
    CategoryCreateSerializer, CategoryListSerializer, GoalCreateSerializer, GoalListSerializer,
    CommentCreateSerializer, CommentListSerializer, BoardCreateSerializer, BoardUpdateSerializer, BoardListSerializer
)


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['title', 'created']
    ordering = ['title']

    _serializers = {
        'create': BoardCreateSerializer,
        'list': BoardListSerializer,
    }
    _default_serializer = BoardUpdateSerializer

    def get_serializer_class(self):
        return self._serializers.get(self.action, self._default_serializer)

    # Переопределяем метод для отображения досок с учетом полей user и is_deleted.
    def get_queryset(self):
        return super().get_queryset().filter(
            participants__user_id=self.request.user.id,
            is_deleted=False
        )

    # Переопределяем метод для добавления в serializer поля user (create).
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Переопределяем метод для добавления в serializer поля user (retrieve, update).
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    # Переопределяем метод для исключения удаления доски из базы.
    def perform_destroy(self, instance: Board) -> Board:
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board_id=instance.id).update(status=Goal.Status.archived)
        return instance


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().select_related('user', 'board')
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrWriter]

    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['board']
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title']

    _serializers = {
        'create': CategoryCreateSerializer,
    }
    _default_serializer = CategoryListSerializer

    def get_serializer_class(self):
        return self._serializers.get(self.action, self._default_serializer)

    # Переопределяем метод для отображения категорий с учетом полей user и is_deleted.
    def get_queryset(self):
        return super().get_queryset().filter(
            board__participants__user_id=self.request.user.id,
            is_deleted=False
        )

    # Переопределяем метод для добавления в serializer поля user.
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
    queryset = Goal.objects.all().select_related('user', 'category')
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrWriter]

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

    # Переопределяем метод для отображения целей с учетом полей user и status.
    def get_queryset(self):
        return super().get_queryset().filter(
            category__board__participants__user_id=self.request.user.id,
            category__is_deleted=False,
            status__lt=Goal.Status.archived,
        )

    # Переопределяем метод для добавления в serializer поля user.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Переопределяем метод для исключения удаления целей из базы.
    def perform_destroy(self, instance: Goal) -> Goal:
        with transaction.atomic():
            instance.status = Goal.Status.archived
            instance.save(update_fields=('status',))
        return instance


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().select_related('goal')
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrWriter]

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
            goal__category__board__participants__user_id=self.request.user.id,
            goal__status__lt=Goal.Status.archived,
        )

    # Переопределяем метод для добавления в serializer поля user.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
