from rest_framework.routers import DefaultRouter

from account.views import UserViewSet

router = DefaultRouter()
router.register(r'api/user', UserViewSet)
account_urlpatterns = router.urls