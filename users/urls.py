from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'payments', views.PaymentViewSet, basename='payment')

urlpatterns = [
    path('register/', views.UserCreateView.as_view(), name='user-register'),
    path('<int:id>/', views.UserProfileRetrieveUpdateView.as_view(), name='user-detail'),
    path('', views.UserListView.as_view(), name='user-list'),
    # Включаем URL-ы от router
    path('', include(router.urls)),
]
