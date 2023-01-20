from rest_framework import serializers

from core.serializers import ProfileSerializer
from goals.models import Category, Goal


class CategoryCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default='author')

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'author', 'is_deleted',)


class CategoryListSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'author',)


class GoalCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default='author')

    def validate_category(self, value: Category):
        # Проверка статуса категории 'Удалена'
        if value.is_deleted:
            raise serializers.ValidationError('not allowed in deleted category')
        # Проверка категории на авторство
        if value.author != self.context['request'].user:
            raise serializers.ValidationError('not owner of category')

        return value

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'author',)


class GoalListSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'author',)
