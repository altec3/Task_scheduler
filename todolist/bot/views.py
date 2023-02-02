from rest_framework import permissions, generics, mixins

from bot.models import TgUser
from bot.serializers import TgUserSerializer


class TgUserUpdateView(mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = TgUser.objects.all()
    model = TgUser
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TgUserSerializer

    # Переопределяем метод для получения объекта TgUser не по pk, а по полю 'verification_code'
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {'verification_code': self.request.data['verification_code']}
        obj = generics.get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    # Реализуем метод PATCH
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
