import djoser.serializers as djs
from rest_framework import serializers

from user.models import CustomUser
from user.models import Follower


class UserCreateSerializer(djs.UserCreateSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserSerializer(djs.UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        ref_name = 'CustomUserSerializer'

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return Follower.objects.filter(
            followed_user=request.user, following_user=obj
        ).exists()
