from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from base.models import Room, Topic, User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class FullUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'last_login', 'first_name', 'last_name', 'is_active', 'date_joined')


class HostSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class TopicSerializer(ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id', 'name')


class RoomSerializer(ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    host = UserSerializer(many=False, read_only=True)
    topic = TopicSerializer(many=False, read_only=True)

    class Meta:
        model = Room
        fields = ('id', 'name', 'description', 'created', 'updated', 'host', 'participants', 'topic')
