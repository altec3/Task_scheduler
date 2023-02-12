from rest_framework import permissions, generics, mixins

from bot.models import TgUser
from bot.serializers import TgUserSerializer
from bot.tg.client import TgClient
from todolist import settings


class TgUserUpdateView(mixins.UpdateModelMixin, generics.GenericAPIView):
    """Представление для обработки запросов на эндпоинт PATCH: /bot/verify

    Верификация пользователя в Telegram чате
    """

    queryset = TgUser.objects.all()
    model = TgUser
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TgUserSerializer

    #: Переопределяем метод для получения объекта TgUser не по pk, а по полю 'verification_code'
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {'verification_code': self.request.data['verification_code']}
        obj = generics.get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    #: Реализуем метод PATCH
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    #: Переопределяем метод для реализации отправки сообщения об удачной верификации Telegram пользователя
    def perform_update(self, serializer):
        tg_user: TgUser = serializer.save()
        TgClient(token=settings.TG_TOKEN).send_message(
            chat_id=tg_user.tg_id,
            text='[verification was successful]'
        )
