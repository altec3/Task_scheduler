from rest_framework import serializers

from core.serializers import ProfileSerializer
from goals.models import Category, Goal, Comment


class CategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default='user')

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted',)


class CategoryListSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user',)


class GoalCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default='user')

    def validate_category(self, value: Category):
        # Проверка статуса категории 'Удалена'
        if value.is_deleted:
            raise serializers.ValidationError('not allowed in deleted category')
        # Проверка категории на авторство
        if value.user != self.context['request'].user:
            raise serializers.ValidationError('not owner of category')

        return value

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user',)


class GoalListSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user',)


class CommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default='user')

    def validate_goal(self, value: Goal) -> Goal:
        # Проверка статуса цели 'Архив'
        if value.status == Goal.Status.archived:
            raise serializers.ValidationError('not allowed in archived goal')
        # Проверка цели на авторство
        if value.user != self.context['request'].user:
            raise serializers.ValidationError('not owner of goal')

        return value

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated',)


class CommentListSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'goal',)
