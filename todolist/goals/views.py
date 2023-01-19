from rest_framework import viewsets, filters, pagination, permissions

from goals.models import Category
from goals.permissions import IsOwnerOrStaff
from goals.serializers import CategoryCreateSerializer, CategoryListSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().select_related("author")
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title"]

    _serializers = {
        "create": CategoryCreateSerializer,
    }
    _default_serializer = CategoryListSerializer

    _permissions = {
        "create": [permissions.IsAuthenticated()],
    }
    _default_permissions = [permissions.IsAuthenticated(), IsOwnerOrStaff()]

    def get_serializer_class(self):
        return self._serializers.get(self.action, self._default_serializer)

    def get_permissions(self):
        return self._permissions.get(self.action, self._default_permissions)

    # Переопределяем метод для отображения категорий с учетом полей author и is_deleted.
    def get_queryset(self):
        return Category.objects.filter(author=self.request.user, is_deleted=False)

    # Переопределяем метод для добавления в serializer поля с автором.
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # Переопределяем метод для исключения удаления категории из базы.
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        return instance
