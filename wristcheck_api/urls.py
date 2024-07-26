"""wristcheck_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework.routers import DefaultRouter

from account.views import UserViewSet
from track.views import WatchVisitRecordViewSet
from wishlist.views import WishlistViewSet

urlpatterns = [
    # path('', lambda request: HttpResponse("Welcome to the Homepage!"), name='home'),
    path("admin/", admin.site.urls),
    path("drf-admin/", include("rest_framework.urls", namespace="rest_framework")),
    path("doc/schema", SpectacularAPIView.as_view(), name="schema"),
    path(
        "doc/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("doc/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("sentry-debug/", lambda request: 1 / 0),  # 触发sentry异常
]

router = DefaultRouter()
router.register(r"user", UserViewSet)
router.register(r"wishlist", WishlistViewSet)
router.register(r"track/watch-visit", WatchVisitRecordViewSet)
urlpatterns.extend(router.urls)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
