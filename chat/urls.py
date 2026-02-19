from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('<str:username>/', views.chat_room, name='chat_room'),
]
