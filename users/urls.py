from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.UserCreateView.as_view(), name='user-register'),
    path('<int:id>/', views.UserProfileRetrieveUpdateView.as_view(), name='user-detail'),
    path('', views.UserListView.as_view(), name='user-list'),
]
