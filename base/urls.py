from django.urls import path
from django.views.generic import TemplateView

from . import views
from .views import EmailVerify

urlpatterns = [
    path('set_theme', views.set_theme, name='set-theme'),

    path('login', views.login_page, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('register', views.register_page, name='register'),

    # email confirmation
    path('confirm_email/', TemplateView.as_view(template_name='confirm_email.html'), name='confirm-email'),
    path('verify_email/<uidb64>/<token>/', EmailVerify.as_view(), name='verify-email'),

    path('invalid_verify/',
         TemplateView.as_view(template_name='invalid_verify.html'), name='invalid-verify'),

    # password change
    path('password-change/', views.password_change, name='password-change'),
    #path('verify_password/<uidb64>/<token>/', PasswordChangeVerify.as_view(), name='verify-password'),

    path('', views.home, name='home'),
    path('room/<str:pk>', views.room, name='room'),
    path('profile/<str:pk>', views.user_profile, name='user-profile'),

    path('create-room/', views.create_room, name='create-room'),
    path('update-room/<str:pk>', views.update_room, name='update-room'),
    path('delete-room/<str:pk>', views.delete_room, name='delete-room'),
    path('delete-message/<str:pk>', views.delete_message, name='delete-message'),

    path('update-user', views.update_user, name='update-user'),

    path('topics', views.topics_page, name='topics-page'),
    path('activities', views.activities_page, name='activities-page'),
]
