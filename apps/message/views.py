from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import User
from apps.message.models import Message


@login_required(login_url="login")
def chats(request, recipient_id):
    recipient = get_object_or_404(User, pk=recipient_id)
    if recipient.pk == request.user.pk:
        return redirect("list_chat")

    conversation = Message.objects.filter(
        Q(sender=request.user, recipient=recipient)
        | Q(sender=recipient, recipient=request.user)
    ).select_related("sender", "recipient").order_by("timestamp")

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                content=content[:5000],
            )
        return redirect("chats", recipient_id=recipient.pk)

    return render(request, "chat.html", {"recipient": recipient, "messages": conversation})


@login_required(login_url="login")
def user_chats(request):
    sent_to = Message.objects.filter(sender=request.user).values_list("recipient_id", flat=True)
    received_from = Message.objects.filter(recipient=request.user).values_list("sender_id", flat=True)
    partner_ids = set(sent_to) | set(received_from)
    users = User.objects.filter(pk__in=partner_ids).order_by("username")

    chats = []
    for partner in users:
        latest_message = (
            Message.objects.filter(
                Q(sender=request.user, recipient=partner)
                | Q(sender=partner, recipient=request.user)
            )
            .order_by("-timestamp")
            .first()
        )
        if latest_message is not None:
            chats.append({"user": partner, "latest_message": latest_message})

    chats.sort(key=lambda item: item["latest_message"].timestamp, reverse=True)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "chats": [
                {
                    "user_id": item["user"].pk,
                    "username": item["user"].username,
                    "content": item["latest_message"].content,
                    "timestamp": item["latest_message"].timestamp.isoformat(),
                }
                for item in chats
            ]
        })

    return render(request, "list_chats.html", {"chats": chats})


@login_required(login_url="login")
def messages_view(request):
    messages = (
        Message.objects.filter(Q(sender=request.user) | Q(recipient=request.user))
        .select_related("sender", "recipient")
        .order_by("-timestamp")
    )
    partners = User.objects.filter(
        Q(sent_messages__recipient=request.user)
        | Q(received_messages__sender=request.user)
    ).distinct()
    return render(
        request,
        "messages_search.html",
        {
            "messages": messages,
            "user": request.user,
            "senders": partners,
            "recipients": partners,
        },
    )
