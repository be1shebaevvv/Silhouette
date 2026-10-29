from django.urls import path

from apps.accounts import views

urlpatterns = [
    path("profil/", views.profil, name="profil"),
    path("login", views.LoginView.as_view(), name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/done/", views.RegisterDoneView.as_view(), name="register_done"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("profile/<str:username>/", views.show_profile, name="profile"),
    path("subscribe/<int:user_id>/", views.subscribe, name="subscribe"),
    path("unsubscribe/<int:user_id>/", views.unsubscribe, name="unsubscribe"),
    path("block/<int:user_id>/", views.block_user, name="block_user"),
    path("unblock/<int:user_id>/", views.unblock_user, name="unblock_user"),
    path("followers/list/<str:username>/", views.followers_view, name="followers"),
    path("subscriptions/<str:username>/", views.subscription_list, name="subscription_list"),
    path("searh/user/", views.search_results, name="search"),
    path("register/confirm/<str:uidb64>/<str:token>/", views.activate_account, name="account_activate"),
]
