from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserSearchViewSet, FriendRequestViewSet, SignupView, LoginView

router = DefaultRouter()
router.register(r'users', UserSearchViewSet)
router.register(r'friend-requests', FriendRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
]
