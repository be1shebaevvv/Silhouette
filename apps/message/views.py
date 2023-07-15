from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from .models import Message
from apps.accounts.models import User
from datetime import datetime
from django.db.models import Q





@login_required(login_url='login')
def chats(request, recipient_id):
    recipient = get_object_or_404(User, pk=recipient_id)
    
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=recipient) | Q(sender=recipient, recipient=request.user)
    ).order_by('-timestamp')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, recipient=recipient, content=content)
            return redirect('chats', recipient_id=recipient_id)

    return render(request, 'chat.html', {'recipient': recipient, 'messages': messages})






    






@login_required(login_url='login')
def my_view(request):
    user = request.user
    request.user.last_seen = datetime.now()
    request.user.save()
    context = {'user': user}
    return render(request, 'chat.html', context)



@login_required(login_url='login')
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
    chats = sorted(chats, key=lambda x: x['latest_message'].timestamp, reverse=True)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = {'chats': chats}
        return JsonResponse(data)

    return render(request, 'list_chats.html', {'chats': chats})




# поиск собеседника

def messages_view(request):
    user = request.user
    messages = Message.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('-timestamp')
    senders = User.objects.filter(
        Q(sent_messages__in=messages) | Q(received_messages__in=messages)
    ).distinct()
    recipients = User.objects.filter(
        Q(sent_messages__in=messages) | Q(received_messages__in=messages)
    ).distinct()
    context = {
        'messages': messages,
        'user': user,  
        'senders': senders,  
        'recipients': recipients  
    }
    return render(request, 'messages_search.html', context)




