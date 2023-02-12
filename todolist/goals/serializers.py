from django.db import transaction
from rest_framework import serializers, exceptions

from core.models import User
from core.serializers import ProfileSerializer
from goals.models import Category, Goal, Comment, Board, BoardParticipant


class BoardCreateSerializer(serializers.ModelSerializer):
    """Сериализатор представления BoardViewSet

    Action create
    """
    user = serializers.HiddenField(default='user')

    #: Добавление текущего пользователя владельцем в список участников доски
    def create(self, validated_data) -> Board:
        user = validated_data.pop('user')
        board = Board.objects.create(**validated_data)
        BoardParticipant.objects.create(user=user, board=board, role=BoardParticipant.Role.owner)
        return board

    class Meta:
        model = Board
        read_only_fields = ('id', 'created', 'updated', 'is_deleted',)
        fields = '__all__'


class BoardParticipantSerializer(serializers.ModelSerializer):
    """Сериализатор модели BoardParticipant

    Для преобразования данных об участниках доски
    """
    role = serializers.ChoiceField(required=True, choices=BoardParticipant.Role.choices[1:])
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = BoardParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board',)


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор представления BoardViewSet

    Actions: update, retrieve, partial_update, destroy
    """
    participants = BoardParticipantSerializer(many=True)
    user = serializers.HiddenField(default='user')

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated',)

    #: Реализация частичного обновления доски
    def update(self, instance: Board, validated_data: dict) -> Board:
        owner = validated_data.pop('user')
        if new_participants := validated_data.get('participants'):
            new_by_id = {part['user'].id: part for part in new_participants}
            old_participants = instance.participants.exclude(user=owner)
            with transaction.atomic():
                for old_participant in old_participants:
                    if old_participant.user_id not in new_by_id:
                        old_participant.delete()
                    else:
                        if old_participant.role != new_by_id[old_participant.user_id]['role']:
                            old_participant.role = new_by_id[old_participant.user_id]['role']
                            old_participant.save()
                        new_by_id.pop(old_participant.user_id)
                for new_part in new_by_id.values():
                    BoardParticipant.objects.create(
                        user=new_part['user'], board=instance, role=new_part['role']
                    )
        if title := validated_data.get('title'):
            instance.title = title

        instance.save()

        return instance


class BoardListSerializer(serializers.ModelSerializer):
    """Сериализатор представления BoardViewSet

    Action list
    """
    class Meta:
        model = Board
        fields = '__all__'


class CategoryCreateSerializer(serializers.ModelSerializer):
    """Сериализатор представления CategoryViewSet

    Action create
    """
    user = serializers.HiddenField(default='user')

    def validate_board(self, value: Board) -> Board:
        #: Проверка статуса доски
        if value.is_deleted:
            raise serializers.ValidationError('Not allowed in deleted category')
        #: Проверка роли пользователя
        if not value.participants.filter(
            user_id=self.context['request'].user.id,
            role__in=(BoardParticipant.Role.owner, BoardParticipant.Role.writer,)
        ).exists():
            raise exceptions.PermissionDenied

        return value

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted',)


class CategoryListSerializer(serializers.ModelSerializer):
    """Сериализатор представления CategoryViewSet

    Actions: list, update, retrieve, partial_update, destroy
    """
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'board',)


class GoalCreateSerializer(serializers.ModelSerializer):
    """Сериализатор представления GoalViewSet

    Action create
    """
    user = serializers.HiddenField(default='user')

    def validate_category(self, value: Category) -> Category:
        #: Проверка статуса категории
        if value.is_deleted:
            raise serializers.ValidationError('Not allowed in deleted category')
        #: Проверка роли пользователя
        if not value.board.participants.filter(
                user_id=self.context['request'].user.id,
                role__in=(BoardParticipant.Role.owner, BoardParticipant.Role.writer,)
        ).exists():
            raise exceptions.PermissionDenied

        return value

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user',)


class GoalListSerializer(serializers.ModelSerializer):
    """Сериализатор представления GoalViewSet

    Actions: list, update, retrieve, partial_update, destroy
    """
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user',)


class CommentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор представления CommentViewSet

    Action create
    """
    user = serializers.HiddenField(default='user')

    def validate_goal(self, value: Goal) -> Goal:
        #: Проверка статуса цели
        if value.status == Goal.Status.archived:
            raise serializers.ValidationError('Not allowed in archived goal')
        #: Проверка роли пользователя
        if not value.category.board.participants.filter(
                user_id=self.context['request'].user.id,
                role__in=(BoardParticipant.Role.owner, BoardParticipant.Role.writer,)
        ).exists():
            raise exceptions.PermissionDenied

        return value

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated',)


class CommentListSerializer(serializers.ModelSerializer):
    """Сериализатор представления CommentViewSet

    Actions: list, update, retrieve, partial_update, destroy
    """
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'goal',)
