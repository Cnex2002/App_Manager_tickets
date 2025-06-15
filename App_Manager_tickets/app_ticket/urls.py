from django.urls import path
from . import views

urlpatterns = [
    path('chatbox/', views.chatbox_view, name='chatbox'),
    path('chatbox/query/', views.chatbox_query, name='chatbox_query'),
]
