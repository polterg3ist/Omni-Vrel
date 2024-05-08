from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q, Count
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.utils.http import urlsafe_base64_decode
from django.views import View

from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from .utils import is_message_valid, send_email_for_verify
import json
# Create your views here.

# langs = ['Python', 'C#', 'JavaScript', 'C++', 'Lua', 'Java', 'C']
# rooms = [
#     {'id': room_id, 'name': f'Lets learn {langs[room_id]}!'} for room_id in range(len(langs))
# ]


def set_theme(request):
    if request.method == 'POST':
        theme_color = json.load(request)['color']
        print(theme_color)
        request.session['theme_mode'] = theme_color
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        #return redirect('home')


def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            # if there is no user with this email it will drop an error
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Wrong email or password')
        else:
            # if password is correct and email is verified authenticate user
            if check_password(password, user.password):
                if not user.email_verify:
                    send_email_for_verify(request, user)
                    messages.error(request, 'You need to verify your email before logging in.')
                else:
                    user = authenticate(request, email=email, password=password)
                    login(request, user)
                    return redirect('home')
            else:
                messages.error(request, 'Wrong email or password')

    # will work if request is GET or authentication failed
    context = {'page': page}
    return render(request, 'login_register.html', context)


def logout_user(request):
    logout(request)
    return redirect('home')


def register_page(request):
    form = MyUserCreationForm()

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.username = user.username.lower()
            # user.save()
            # login(request, user)
            # return redirect('home')
            send_email_for_verify(request, user, subject='email')
            return redirect('confirm-email')
        else:
            messages.error(request, "An error occurred during registration")
    return render(request, 'login_register.html', {'form': form})


class EmailVerify(View):

    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)

        if user is not None and token_generator.check_token(user, token):
            user.email_verify = True
            user.save()
            login(request, user)
            return redirect('home')
        return redirect('invalid_verify')

    @staticmethod
    def get_user(uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
            ValidationError,
        ):
            user = None
        return user


def password_change(request):
    send_email_for_verify(request, request.user, subject='password')
    return render(request, 'confirm_password.html')


def home(request):
    q = request.GET.get('q')
    topic = request.GET.get('topic')

    if q:
        rooms = Room.objects.filter(
            Q(topic__name__contains=q) |
            Q(name__contains=q) |
            Q(description__contains=q) |
            Q(host__username__contains=q)
        )
        room_messages = Message.objects.filter(
            Q(room__topic__name__contains=q) |
            Q(room__name__contains=q) |
            Q(room__description__contains=q)
        )[:5]

        query_name = q[:25]
    elif topic:
        rooms = Room.objects.filter(
            Q(topic__name=topic)
        )
        room_messages = Message.objects.filter(
            Q(room__topic__name__contains=topic)
        )[:5]

        query_name = topic
    else:
        rooms = Room.objects.all()
        room_messages = Message.objects.all()[:5]

        query_name = 'All'

    room_count = rooms.count()
    topics = Topic.objects.annotate(max_count=Count("room")).order_by('-max_count')[0:10]

    context = {'rooms': rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages,
               'query_name': query_name
               }
    return render(request, 'base/home.html', context)


def room(request, pk):
    if not pk.isdigit():
        return HttpResponse('<h1>Error 404 (Page not found)</h1><p>It looks like you wanted go to specific room but mistyped a letter in URL<p>There is no letters in rooms URL</p>', status=404)
    try:
        room = Room.objects.get(id=pk)
        room_messages = room.message_set.all().order_by('-created')
        participants = room.participants.all()
        if request.method == "POST":
            message_body = request.POST.get('body')
            if is_message_valid(message_body):
                message = Message.objects.create(
                    user=request.user,
                    room=room,
                    body=message_body,
                )
            else:
                messages.error(request, "Your message is blank or too long!")
            room.participants.add(request.user)
            return redirect('room', pk=room.id)
        context = {'room': room, 'room_messages': room_messages, 'participants': participants}
        return render(request, 'room.html', context)
    except Room.DoesNotExist:
        return HttpResponse('<h1>Error 404 (Page not found)</h1>', status=404)


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    user_messages = user.message_set.all()[:10]
    topics = Topic.objects.all()

    # in template user_messages variable called room_messages, so
    # it's why key name and value name in dictionary didn't match
    context = {'user': user, 'rooms': rooms, 'room_messages': user_messages, 'topics': topics}
    return render(request, 'profile.html', context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room = Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )

        room.participants.add(request.user)
        # if form.is_valid():
        #
        #     room = form.save()  # it saves and returns model
        #     room.host = request.user
        #     room.participants.add(request.user)
        #     room.save()
        return redirect('room', pk=room.id)
    context = {'form': form, "topics": topics}
    return render(request, 'room_form.html', context)


@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    topics = Topic.objects.all()
    form = RoomForm(instance=room)

    if request.user != room.host and not request.user.is_staff:
        return HttpResponse('You are not allowed here!!', status=403)

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'room_form.html', context)


@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host and not request.user.is_staff:
        return HttpResponse('You are not allowed here!!', status=403)

    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'delete.html', {'obj': room})


@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user and not request.user.is_staff:
        return HttpResponse('You are not allowed here!!', status=403)

    if request.method == "POST":
        message.delete()
        return redirect('room', pk=message.room.id)
    return render(request, 'delete.html', {'obj': message})


@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)
    context = {'form': form}

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            # if email is unchanged
            if user.email == form.cleaned_data.get('email'):
                form.save()
                return redirect('user-profile', pk=user.id)
            else:
                send_email_for_verify(request, user)
                return redirect('confirm-email')

    return render(request, 'update-user.html', context)


def topics_page(request):
    q = request.GET.get('q')
    if q:
        topics = Topic.objects.filter(name__contains=q)
    else:
        topics = Topic.objects.annotate(max_count=Count("room")).order_by('-max_count')

    return render(request, 'base/topics.html', {'topics': topics})


def activities_page(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})
