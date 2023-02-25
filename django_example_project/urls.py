"""django_example_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path("", views.home, name="home")
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path("", Home.as_view(), name="home")
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path("blog/", include("blog.urls"))
"""

from catalog.views import RegisterFormView, UpdateProfile, UserProfile

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(url="/catalog/")),
    path("admin/", admin.site.urls),
    path("catalog/", include("catalog.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", RegisterFormView.as_view(), name="register"),
    path("accounts/update_profile/", UpdateProfile.as_view(), name="update_profile"),
    path("accounts/my_profile/", UserProfile.as_view(), name="profile"),
    path("example/", include("example.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    # fmt: off
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        path("silk/", include("silk.urls", namespace="silk")),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # noqa: E501
    # fmt: on
