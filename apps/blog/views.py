from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.accounts.models import User
from apps.blog.forms import CommentForm, PostCreationForm, PostForm
from apps.blog.models import Comment, Post


class PostListViews(ListView):
    template_name = "index.html"
    model = Post
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        return (
            Post.objects.filter(is_active=True)
            .select_related("author", "category")
            .prefetch_related("likes", "dislikes", "post_comments")
            .order_by("-created_at")
        )


def listviews(request):
    return render(request, "index1.html")


class RecomentPost(ListView):
    template_name = "post_recommendations.html"
    model = Post
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        return (
            Post.objects.filter(is_active=True)
            .select_related("author", "category")
            .order_by("?")
        )


class UserPosts(ListView):
    model = Post
    template_name = "post_user.html"
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs["user_id"])
        return Post.objects.filter(author=user, is_active=True).select_related("category")


@login_required(login_url="login")
def user_post_count(request):
    post_count = Post.objects.filter(author=request.user, is_active=True).count()
    posts = Post.objects.filter(author=request.user, is_active=True).order_by("-created_at")[:4]
    return render(request, "profil.html", {"user": request.user, "posts": posts, "post_count": post_count})


@login_required(login_url="login")
@require_POST
def save_comment_form(request, post_id):
    post = get_object_or_404(Post, pk=post_id, is_active=True)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("post_detail", pk=post.pk)


@login_required(login_url="login")
@require_POST
def reply_to_comment(request, comment_id):
    parent = get_object_or_404(Comment.objects.select_related("post"), pk=comment_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.author = request.user
        reply.post = parent.post
        reply.parent_comment = parent
        reply.save()
    return redirect("post_detail", pk=parent.post.pk)


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = "post_create.html"
    model = Post
    success_url = reverse_lazy("all")
    form_class = PostCreationForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Post
    template_name = "post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(is_active=True).select_related("author", "category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        context["comments"] = (
            Comment.objects.filter(post=post, parent_comment__isnull=True)
            .select_related("author")
            .prefetch_related("replies__author")
        )
        context["comment_count"] = Comment.objects.filter(post=post).count()
        context["like_count"] = post.likes.count()
        context["dislike_count"] = post.dislikes.count()
        return context


@login_required(login_url="login")
def add_post(request):
    if request.method == "POST":
        form = PostCreationForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostCreationForm()
    return render(request, "post_create.html", {"form": form})


@login_required(login_url="login")
@require_POST
def like_dislike_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, is_active=True)
    action = request.POST.get("action")

    if action == "like":
        if post.likes.filter(pk=request.user.pk).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
            post.dislikes.remove(request.user)
    elif action == "dislike":
        if post.dislikes.filter(pk=request.user.pk).exists():
            post.dislikes.remove(request.user)
        else:
            post.dislikes.add(request.user)
            post.likes.remove(request.user)

    return redirect("post_detail", pk=post.pk)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "post_edit.html"

    def test_func(self):
        return self.get_object().author_id == self.request.user.pk

    def get_success_url(self):
        return reverse("post_detail", kwargs={"pk": self.object.pk})


@login_required(login_url="login")
def feed(request):
    subscribed_users = request.user.subscriptions.all()
    posts = (
        Post.objects.filter(author__in=subscribed_users, is_active=True)
        .select_related("author", "category")
        .prefetch_related("likes", "post_comments")
        .order_by("-created_at")
    )
    return render(request, "feed.html", {"posts": posts})


def top_posts_view(request):
    top_posts = (
        Post.objects.filter(is_active=True)
        .annotate(like_count=Count("likes", distinct=True))
        .order_by("-like_count", "-created_at")[:3]
    )
    return render(request, "index1.html", {"top_posts": top_posts})
