from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from base.models import Room, User
from .serializers import RoomSerializer, UserSerializer, FullUserSerializer


@api_view(['GET'])
def get_routes(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id',
        'GET /api/users',
        'GET /api/users/:id',
    ]

    return Response(routes)


@api_view(['GET'])
def get_rooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_room(request, pk):
    try:
        room = Room.objects.get(id=pk)
    except Room.DoesNotExist:
        return Response([f'There is no room with id={pk}'])
    serializer = RoomSerializer(room)
    return Response(serializer.data)


@api_view(['GET'])
def get_users(request):
    users = User.objects.all()
    serializer = FullUserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_user(request, pk):
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        return Response([f'There is no user with id={pk}'])
    serializer = FullUserSerializer(user)
    return Response(serializer.data)
