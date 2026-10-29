import re

from django.contrib import messages as flash_messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, FormView, TemplateView

from apps.accounts.forms import DeleteAccountForm, LoginForm, UserProfileForm, UserRegisterForm
from apps.accounts.models import User
from apps.accounts.token import CustomTokenGenerator
from apps.accounts.utils import send_activation_email
from apps.blog.models import Post


@method_decorator(ratelimit(key="ip", rate="10/m", method="POST", block=True), name="dispatch")
class LoginView(FormView):
    template_name = "login.html"
    form_class = LoginForm

    def form_valid(self, form):
        user = authenticate(
            self.request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        if user is None:
            form.add_error(None, "Неверный никнейм или пароль.")
            return self.form_invalid(form)
        if not user.is_active:
            form.add_error(None, "Этот аккаунт отключён.")
            return self.form_invalid(form)
        if not user.is_verified:
            form.add_error(None, "Подтвердите адрес электронной почты по ссылке из письма.")
            return self.form_invalid(form)

        login(self.request, user)
        return redirect("feed")


@require_POST
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("login")


class RegisterDoneView(TemplateView):
    template_name = "register_done.html"


@method_decorator(ratelimit(key="ip", rate="3/h", method="POST", block=True), name="dispatch")
class UserRegisterView(CreateView):
    model = User
    template_name = "register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("register_done")

    def form_valid(self, form):
        nickname = form.cleaned_data["username"]
        if not re.fullmatch(r"[a-zA-Z0-9_]+", nickname):
            form.add_error(
                "username",
                "Никнейм должен содержать только английские буквы, цифры и знак подчёркивания.",
            )
            return self.form_invalid(form)

        user = form.save(commit=False)
        user.is_verified = False
        user.save()
        form.save_m2m()
        send_activation_email(user, request=self.request, to_email=user.email)

        # CreateView.get_success_url() formats success_url with self.object.
        # This custom form_valid() does not call super(), so self.object is None.
        # Redirecting to success_url directly avoids the None.__dict__ error.
        return redirect(self.success_url)


def profil(request):
    if not request.user.is_authenticated:
        return redirect("login")
    posts = Post.objects.filter(author=request.user).order_by("-created_at")[:4]
    return render(request, "profil.html", {"user": request.user, "posts": posts})


token_generator = CustomTokenGenerator()


def activate_account(request, uidb64, token):
    try:
        user_id = int(force_str(urlsafe_base64_decode(uidb64)))
        user = User.objects.get(pk=user_id)
    except (ValueError, TypeError, OverflowError, User.DoesNotExist):
        raise Http404("Недействительная ссылка подтверждения.")

    if not token_generator.check_token(user, token):
        raise Http404("Ссылка подтверждения недействительна или устарела.")

    user.is_verified = True
    user.save(update_fields=["is_verified"])
    login(request, user)
    return redirect("feed")


@login_required(login_url="login")
def edit_profile(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            previous_email = request.user.email
            updated_user = form.save(commit=False)
            if updated_user.email != previous_email:
                updated_user.is_verified = False
                updated_user.save()
                send_activation_email(updated_user, request=request, to_email=updated_user.email)
                logout(request)
                return redirect("register_done")
            updated_user.save()
            return redirect("profile", username=updated_user.username)
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "edit_profile.html", {"form": form})


def show_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user, is_active=True).order_by("-created_at")
    return render(request, "profil.html", {"user": user, "posts": posts})


@login_required(login_url="login")
@require_POST
def subscribe(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user.pk != request.user.pk:
        if request.user.blocked_users.filter(pk=user.pk).exists() or user.blocked_users.filter(pk=request.user.pk).exists():
            flash_messages.error(request, "Подписка недоступна из-за настроек блокировки.")
        else:
            user.followers.add(request.user)
            request.user.subscriptions.add(user)
    return redirect("profile", username=user.username)


@login_required(login_url="login")
@require_POST
def unsubscribe(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.followers.remove(request.user)
    request.user.subscriptions.remove(user)
    return redirect("profile", username=user.username)

@login_required(login_url="login")
@require_POST
def block_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user.pk != request.user.pk:
        request.user.blocked_users.add(user)
        request.user.subscriptions.remove(user)
        user.followers.remove(request.user)
        request.user.followers.remove(user)
        user.subscriptions.remove(request.user)
        flash_messages.success(request, "Пользователь заблокирован. Переписка и подписка отключены.")
    return redirect("profile", username=user.username)


@login_required(login_url="login")
@require_POST
def unblock_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    request.user.blocked_users.remove(user)
    flash_messages.success(request, "Пользователь разблокирован.")
    return redirect("profile", username=user.username)


def subscription_list(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, "subscription_list.html", {"subscriptions": user.subscriptions.all()})


def followers_view(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, "user_followers.html", {"followers": user.followers.all()})


def search_results(request):
    query = request.GET.get("query", "").strip()
    category = request.GET.get("category", "").strip()

    users = User.objects.none()
    if query:
        users = User.objects.filter(username__icontains=query)
        if request.user.is_authenticated:
            users = users.exclude(pk=request.user.pk)

    posts = Post.objects.filter(is_active=True)
    if category:
        posts = posts.filter(category__name=category)
    elif not query:
        posts = posts.none()
    elif query:
        posts = posts.filter(title__icontains=query) | posts.filter(description__icontains=query)

    return render(
        request,
        "search.html",
        {"users": users, "posts": posts.distinct(), "category": category, "query": query},
    )



@login_required(login_url="login")
@require_POST
def delete_account(request):
    form = DeleteAccountForm(request.POST)
    if not form.is_valid() or not request.user.check_password(form.cleaned_data["password"]):
        flash_messages.error(request, "Аккаунт не удалён: проверьте текущий пароль.")
        return redirect("edit_profile")

    user = request.user
    logout(request)
    user.delete()
    flash_messages.success(request, "Аккаунт и связанные с ним данные удалены.")
    return redirect("list")
