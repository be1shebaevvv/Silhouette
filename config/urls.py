from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    # Correct route; the legacy spelling remains available for old bookmarks.
    path("accounts/", include("apps.accounts.urls")),
    path("accaunts/", include("apps.accounts.urls")),
    path("", include("apps.blog.urls")),
    path("chat/", include("apps.message.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
