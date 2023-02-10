from rest_framework.permissions import SAFE_METHODS, IsAuthenticated

from goals.models import BoardParticipant, Category, Board, Goal, Comment


class BoardPermissions(IsAuthenticated):
    """Определяет доступ к запросу на эндпоинт /goals/board{/<id>}.

        - просмотр: авторизованные пользователи, добавленные в список участников
        - редактирование: только владелец
    """
    message = 'Delete or edit boards can owners only.'

    def has_object_permission(self, request, view, obj: Board) -> bool:
        _filters: dict = {'user_id': request.user.id}

        if request.method not in SAFE_METHODS:
            _filters['role'] = BoardParticipant.Role.owner

        return obj.participants.filter(**_filters).exists()


class IsOwnerOrWriter(IsAuthenticated):
    """Определяет доступ на редактирование объекта

        - просмотр: все авторизованные пользователи
        - редактирование: только владелец или редактор
    """
    message = 'Delete or edit object can owners or writers only.'
    board = None

    def has_object_permission(self, request, view, obj) -> bool:
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
    """Определяет доступ на редактирование комментария

        - просмотр: все авторизованные пользователи
        - редактирование: только автор
    """
    message = 'Delete or edit comments can owners only.'

    def has_object_permission(self, request, view, obj: Comment) -> bool:
        return any((
            request.method in SAFE_METHODS,
            obj.user.id == request.user.id
        ))
