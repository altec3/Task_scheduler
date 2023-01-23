from rest_framework.permissions import BasePermission, SAFE_METHODS

from goals.models import BoardParticipant, Category, Board, Goal, Comment


class BoardPermissions(BasePermission):
    message = 'Delete or edit boards can owners only.'

    def has_object_permission(self, request, view, obj: Board):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user, board=obj
            ).exists()
        return BoardParticipant.objects.filter(
            user=request.user, board=obj, role=BoardParticipant.Role.owner
        ).exists()


class IsOwnerOrWriter(BasePermission):
    message = 'Delete or edit object can owners or writers only.'
    board = None

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if isinstance(obj, Category):
            self.board = obj.board
        elif isinstance(obj, Goal):
            self.board = obj.category.board
        elif isinstance(obj, Comment):
            self.board = obj.goal.category.board
        else:
            return False

        if request.method in SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user,
                board=self.board
            ).exists()

        return BoardParticipant.objects.filter(
            user=request.user,
            board=self.board,
            role__in=(BoardParticipant.Role.owner, BoardParticipant.Role.writer,)
        ).exists()
