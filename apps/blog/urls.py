from  django.urls import path
from apps.blog import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.PostListViews.as_view(), name='all'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name="post_detail"),
    path('recoment/', views.RecomentPost.as_view(), name='recommend_posts'),
    path('post/comment/save/<int:post_id>/', views.save_comment_form, name="save_comment"),
    path('comment/reply/<int:comment_id>/', views.reply_to_comment, name='reply_to_comment'),
    path("post_user/<int:user_id>/", views.UserPosts.as_view(), name="user_post" ),
    path('user/<int:user_id>/post_count/', views.user_post_count, name='post_count'),
    path('add/', views.add_post, name='add_post'),
    path('post/<int:post_id>/like_dislike/', views.like_dislike_post, name='like_dislike_post'),
    path('content/post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post-edit'),
    path('feed/', views.feed, name='feed'),
    path('comment/reply/<int:comment_id>/', views.reply_to_comment, name='reply_to_comment')

]



urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)