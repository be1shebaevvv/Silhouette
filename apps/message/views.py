from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import User
from apps.message.models import Message


@login_required(login_url="login")
def chats(request, recipient_id):
    recipient = get_object_or_404(User, pk=recipient_id)
    if recipient.pk == request.user.pk:
        return redirect("list_chat")
    if (
        request.user.blocked_users.filter(pk=recipient.pk).exists()
        or recipient.blocked_users.filter(pk=request.user.pk).exists()
    ):
        return HttpResponseForbidden("Переписка недоступна из-за настроек блокировки.")

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


def _recent_chats(user):
    sent_to = Message.objects.filter(sender=user).values_list("recipient_id", flat=True)
    received_from = Message.objects.filter(recipient=user).values_list("sender_id", flat=True)
    blocked_ids = set(user.blocked_users.values_list("pk", flat=True))
    blocked_ids.update(user.blocked_by.values_list("pk", flat=True))
    partner_ids = (set(sent_to) | set(received_from)) - blocked_ids
    partners = User.objects.filter(pk__in=partner_ids).order_by("username")

    chats = []
    for partner in partners:
        latest_message = (
            Message.objects.filter(
                Q(sender=user, recipient=partner) | Q(sender=partner, recipient=user)
            )
            .order_by("-timestamp")
            .first()
        )
        if latest_message is not None:
            chats.append({"user": partner, "latest_message": latest_message})

    return sorted(chats, key=lambda item: item["latest_message"].timestamp, reverse=True)


@login_required(login_url="login")
def user_chats(request):
    chats = _recent_chats(request.user)
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
    query = request.GET.get("query", "").strip()
    users = User.objects.none()
    if query:
        blocked_ids = set(request.user.blocked_users.values_list("pk", flat=True))
        blocked_ids.update(request.user.blocked_by.values_list("pk", flat=True))
        users = User.objects.filter(username__icontains=query).exclude(pk=request.user.pk).exclude(pk__in=blocked_ids)[:20]

    return render(
        request,
        "messages_search.html",
        {"users": users, "query": query, "chats": _recent_chats(request.user)},
    )
