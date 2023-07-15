from django.urls import path
from apps.message.views import chats , user_chats, messages_view

urlpatterns = [
    path('chat/<int:recipient_id>/',  chats, name='chats'),
    path('user/list/', user_chats, name = 'list_chat' ),
    path('searh/message/user/', messages_view, name='searchs' )
]
 