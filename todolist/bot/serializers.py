from rest_framework import serializers

from bot.models import TgUser


class TgUserSerializer(serializers.ModelSerializer):
    """Сериализатор представления TgUserUpdateView"""

    #: Переопределяем метод для добавления id текущего пользователя в экземпляр модели TgUser
    def update(self, instance: TgUser, validated_data: dict) -> TgUser:
        user = self.context['request'].user
        instance.user_id = user.id
        instance.save()

        return instance

    class Meta:
        model = TgUser
        fields = '__all__'
        read_only_fields = ('tg_id', 'tg_username', 'verification_code',)
