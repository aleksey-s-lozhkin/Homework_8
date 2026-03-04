from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views
from .views import CustomTokenObtainPairView

router = DefaultRouter()
router.register(r'payments', views.PaymentViewSet, basename='payment')

urlpatterns = [
    # Публичные эндпоинты
    path('register/', views.UserCreateView.as_view(), name='user-register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token-obtain'),

    # Защищенные эндпоинты
    path('me/', views.CurrentUserView.as_view(), name='current-user'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:id>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<int:id>/update/', views.UserUpdateView.as_view(), name='user-update'),
    path('users/<int:id>/delete/', views.UserDeleteView.as_view(), name='user-delete'),

    # Включаем URL от router
    path('', include(router.urls)),
]
