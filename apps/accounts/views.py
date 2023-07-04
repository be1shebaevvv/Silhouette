import datetime
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.generic import FormView, CreateView, TemplateView

from apps.accounts.forms import LoginForm, UserRegisterForm, UserProfileForm
from apps.accounts.models import User
from apps.accounts.token import CustomTokenGenerator
from apps.accounts.utils import send_activation_email
from apps.blog.views import Post

class LoginView(FormView):
    template_name = "login.html"
    form_class = LoginForm

    def form_valid(self, form):
        data = form.cleaned_data
        username = data["username"]
        password = data["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
                return redirect("recommend_posts")
            else:
                return HttpResponse("Ваш аккаунт не активен")
        return HttpResponse("Такого пользователя не существует или данные неверны")

def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("login")    

class RegisterDoneView(TemplateView):
    template_name = "register_done.html"




from django.urls import reverse_lazy

class UserRegisterView(CreateView):
    model = User
    template_name = "register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("register_done")

    def form_valid(self, form):
        user = form.save()
        send_activation_email(user,request=self.request, to_email=user.email)
        return super().form_valid(form)



class RegisterDoneView(TemplateView):
    template_name = "register_done.html"


def profil(request,):
    return render(request, "profil.html")



def my_view(request):
    instance = User.objects.get(id=1)  
    context = {'instance': instance}  
    return render(request, '', context)



def user_profile(request , user_id):
    user = User.objects.get(id=request.user.id)  
    other_files = user.other_files.all()  
    default_image = 'silhouette/media_sites/defolt_user_images.png'
    context = {
        'user': user,
        'other_files': other_files,
        'default_image': default_image

    }
    
    
    profile_rendered = render(request, 'profile.html', context)
    files_rendered = render(request, 'index.html', context)
    return profile_rendered, files_rendered




token_generator = CustomTokenGenerator()

def activate_account(request,uidb64, token):
    try:
        uid = int(force_str(urlsafe_base64_decode(uidb64)))
        user = User.objects.get(id=uid)
    except (ValueError, User.DoesNotExist, TypeError):
        user = None
    if user is not None and token_generator.check_token(user, token):
        user.is_verified = True
        login(request, user)
        return redirect(reverse_lazy('all'))
    raise Http404


def profile_view(request):
    user = request.user
    posts = Post.objects.filter(author=user).order_by('-created_at')[:4]
    return render(request, 'profil.html', {'posts': posts})



def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)

    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'edit_profile.html', {'form': form})

def show_profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'profil.html', {'user': user})




@login_required(login_url='login')
def subscribe(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.followers.add(request.user)
    request.user.subscriptions.add(user)
    user.save()
    request.user.save()
    return redirect('profile', username=user.username)



@login_required(login_url='login')
def unsubscribe(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.followers.remove(request.user)
    request.user.subscriptions.remove(user)
    user.save()
    request.user.save()
    return redirect('profile', username=user.username)








def subscription_list(request, username):
    # Получаем текущего пользователя (можете использовать другой способ, если у вас есть аутентификация)
    user = User.objects.get(username=username)
    
    # Получаем все подписки текущего пользователя
    subscriptions = user.subscriptions.all()
    
    # Передаем подписки в контекст для отображения в шаблоне
    context = {'subscriptions': subscriptions}
    
    return render(request, 'subscription_list.html', context)



def followers_view(request, username):
    user = User.objects.get(username=username)
    followers = user.followers.all()
    context = {
        'followers': followers
    }
    return render(request, 'user_followers.html', context)





@login_required
def my_view(request):
    user = request.user
    request.user.last_seen = datetime.now()
    request.user.save()
    context = {'user': user}
    return render(request, 'chat.html', context)