from django.urls import path
from apps.message.views import chats , user_chats

urlpatterns = [
    path('chat/<int:recipient_id>/',  chats, name='chats'),
    path('user/list/', user_chats, name = 'list_chat' )
]
 