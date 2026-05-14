from django.urls import path

from blog import views

urlpatterns = [
    path('posts/', views.PostListAPIView.as_view(), name='post-list'),
    path('posts/<int:pk>/', views.PostDetailAPIView.as_view(), name='post-detail'),
    path('posts/<int:post_pk>/comments/', views.CommentAPIView.as_view(), name='comment-list'),
]