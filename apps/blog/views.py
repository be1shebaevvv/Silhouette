
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.db.models import Count
from django.views.generic import ListView, DetailView, CreateView, UpdateView
import random


from apps.blog.models import Post, Category, Comment
from apps.blog.forms import CommentForm, PostCreationForm, PostForm, ReplayCommentForm
from apps.accounts.models import User

class PostListViews(ListView):
    template_name = "index.html"
    model = Post
    queryset = Post.objects.filter(is_active=True).order_by('-created_at')
    context_object_name = "posts"
    paginate_by = 99999

    def get_queryset(self):
        id = self.request.GET.get('id')
        post = Post.objects.filter(id=id)
        queryset = Post.objects.filter(is_active=True).exclude(id=id)
        queryset = list(post) + list(queryset)
        return queryset


def listviews(request):
    return render(request, 'index1.html')




class RecomentPost(ListView):
    template_name = "post_recommendations.html"
    model = Post
    context_object_name = "posts"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_active=True)
        random_posts = random.sample(list(queryset), len(queryset))
        return random_posts



class UserPosts(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'post_user.html'
    context_object_name = 'posts'
    paginate_by = 99999
    
    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        user = get_object_or_404(User, id=user_id)
        queryset = Post.objects.filter(author=user).order_by('-created_at')
        return queryset


@login_required
def user_post_count(request):
    post_count = Post.objects.filter(author=request.user.post.id).count()
    context = {
        'post_count': post_count
    }
    return render(request, 'profil.html', context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from .models import Comment

@login_required(login_url='login')  # Обновленный декоратор
def save_comment_form(request, post_id):
    if request.method == "POST":
        print(request.POST)
        form = CommentForm(request.POST)
        if form.is_valid():
            post = get_object_or_404(Post, id=post_id)
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    return redirect(reverse_lazy("post_detail", kwargs={"pk":post_id}))



from django.shortcuts import get_object_or_404

def reply_to_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)  # Получить объект комментария

    if request.method == "POST":
        form = ReplayCommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.parent = comment
            reply.post = comment.post  # Присвоить тот же пост, что и у родительского комментария
            reply.save()
            return redirect('post_detail', pk=comment.post.pk)

    form = ReplayCommentForm()
    context = {'form': form}
    return render(request, 'post_detail.html', context)




class PostCreateView(LoginRequiredMixin, CreateView):
    template_name="post_create.html"
    model = Post
    success_url = reverse_lazy("all")
    form_class = PostCreationForm


    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return super().form_valid(form)
    
class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        comments = Comment.objects.filter(post=post)
        comment_count = comments.count()
        context['comments'] = comments
        context['comment_count'] = comment_count
        return context
 


@login_required(login_url='login')  # Обновленный декоратор
def add_post(request):
    if request.method == 'POST':
        form = PostCreationForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # Установка поля автора
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostCreationForm()
    return render(request, 'post_create.html', {'form': form})





@login_required(login_url='login')
def like_dislike_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'like':
            if request.user in post.likes.all():
                post.likes.remove(request.user)
            else:
                post.likes.add(request.user)
                post.dislikes.remove(request.user)
        elif action == 'dislike':
            if request.user in post.dislikes.all():
                post.dislikes.remove(request.user)
            else:
                post.dislikes.add(request.user)
                post.likes.remove(request.user)
    
    like_count = post.likes.count()
    dislike_count = post.dislikes.count()
    
    context = {
        'post': post,
        'like_count': like_count,
        'dislike_count': dislike_count
    }
    return render(request, 'post_detail.html', context)




class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'

    def get_success_url(self):
        return reverse('all')






# лента

def feed(request):
    current_user = request.user
    profile = current_user
    subscribed_users = profile.subscriptions.all()
    posts = Post.objects.filter(author__in=subscribed_users).order_by('-created_at')

    context = {
        'posts': posts
    }

    return render(request, 'feed.html', context)


# Топ 3 поста 



def top_posts_view(request):
    top_posts = Post.objects.order_by('-likes')[:3]
    return render(request, 'index1.html', {'top_posts': top_posts})


