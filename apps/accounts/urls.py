from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from apps.accounts import views
from apps.accounts.forms import VerifiedPasswordResetForm

urlpatterns = [
    path("profil/", views.profil, name="profil"),
    path("login", views.LoginView.as_view(), name="login"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            form_class=VerifiedPasswordResetForm,
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    path("logout/", views.user_logout, name="logout"),
    path("register/done/", views.RegisterDoneView.as_view(), name="register_done"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("delete-account/", views.delete_account, name="delete_account"),
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
