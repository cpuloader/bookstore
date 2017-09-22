from django.contrib.auth import update_session_auth_hash
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'phone', 'cards')
        read_only_fields = ('id',)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.cards = validated_data.get('cards', instance.cards)
        instance.save()

        update_session_auth_hash(self.context.get('request'), instance)
        return instance