from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Message
from apps.accounts.models import User
from datetime import datetime
from django.db.models import Q





@login_required
def chats(request, recipient_id):
    recipient = get_object_or_404(User, pk=recipient_id)
    messages = Message.objects.filter(sender=request.user, recipient=recipient) | \
               Message.objects.filter(sender=recipient, recipient=request.user)
    messages = messages.order_by('-timestamp')  # Сортировка по убыванию времени создания сообщения

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, recipient=recipient, content=content)
            return redirect('chats', recipient_id=recipient_id)  # Перенаправление на страницу с чатом

    return render(request, 'chat.html', {'recipient': recipient, 'messages': messages})






@login_required
def my_view(request):
    user = request.user
    request.user.last_seen = datetime.now()
    request.user.save()
    context = {'user': user}
    # Другой код представления
    return render(request, 'chat.html', context)



@login_required
def user_chats(request):
    user = request.user
    user_chats_sent = Message.objects.filter(sender=user).values_list('recipient', flat=True).distinct()
    user_chats_received = Message.objects.filter(recipient=user).values_list('sender', flat=True).distinct()
    user_ids = list(user_chats_sent) + list(user_chats_received)
    users = User.objects.filter(id__in=user_ids)

    chats = []
    for user in users:
        chat = {}
        chat['user'] = user
        latest_message = Message.objects.filter(
            Q(sender=user, recipient=request.user) | Q(sender=request.user, recipient=user)
        ).latest('timestamp')

        chat['latest_message'] = latest_message
        chats.append(chat)

    # Сортировка чатов по новизне последнего сообщения
    chats = sorted(chats, key=lambda x: x['latest_message'].timestamp, reverse=True)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Если запрос является AJAX-запросом, возвращаем только данные в формате JSON
        data = {'chats': chats}
        return JsonResponse(data)

    return render(request, 'list_chats.html', {'chats': chats})






