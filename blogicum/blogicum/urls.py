from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings

from pages.views import register

handler403 = "pages.views.custom_403"
handler404 = "pages.views.custom_404"
handler500 = "pages.views.custom_500"

urlpatterns = [
    path("", include("blog.urls")),
    path("pages/", include("pages.urls")),
    path("admin/", admin.site.urls),
    path("auth/", include("django.contrib.auth.urls")),
    path("auth/registration/", register, name="registration"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
