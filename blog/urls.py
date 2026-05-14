from django.urls import path

from blog import views

urlpatterns = [
    path('posts/', views.PostListAPIView.as_view(), name='post-list')
]