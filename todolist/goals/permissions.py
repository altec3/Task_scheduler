from rest_framework.permissions import SAFE_METHODS, IsAuthenticated

from goals.models import BoardParticipant, Category, Board, Goal, Comment


class BoardPermissions(IsAuthenticated):
    """
    Разрешает доступ к Доске:
        - просмотр: все пользователи, добавленные в список участников
        - редактирование: только автор
    """
    message = 'Delete or edit boards can owners only.'

    def has_object_permission(self, request, view, obj: Board):
        _filters: dict = {'user_id': request.user.id}

        if request.method not in SAFE_METHODS:
            _filters['role'] = BoardParticipant.Role.owner

        return obj.participants.filter(**_filters).exists()


class IsOwnerOrWriter(IsAuthenticated):
    """
    Разрешает доступ на редактирование объекта только пользователям с ролью автор или редактор
    """
    message = 'Delete or edit object can owners or writers only.'
    board = None

    def has_object_permission(self, request, view, obj):
        _filters: dict = {'user_id': request.user.id}

        if isinstance(obj, Category):
            self.board = obj.board
        elif isinstance(obj, Goal):
            self.board = obj.category.board
        elif isinstance(obj, Comment):
            self.board = obj.goal.category.board
        else:
            return False

        if request.method not in SAFE_METHODS:
            _filters['role__in'] = (BoardParticipant.Role.owner, BoardParticipant.Role.writer,)

        return self.board.participants.filter(**_filters).exists()


class IsCommentOwner(IsAuthenticated):
    """
    Разрешает доступ к комментариям:
        - просмотр: все пользователи
        - редактирование: только автор
    """
    message = 'Delete or edit comments can owners only.'

    def has_object_permission(self, request, view, obj: Comment):
        return any((
            request.method in SAFE_METHODS,
            obj.user.id == request.user.id
        ))
