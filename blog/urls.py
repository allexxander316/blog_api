from django.urls import path, include
from rest_framework.routers import DefaultRouter

from blog import views

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')

urlpatterns = [
    # path('posts/', views.PostViewSet.as_view(), name='post-list'),
    # path('posts/<int:pk>/', views.PostViewSet.as_view(), name='post-detail'),
    path('', include(router.urls)),
    path('posts/<int:post_pk>/comments/', views.CommentAPIView.as_view(), name='comment-list'),
    path('posts/<int:post_pk>/comments/<int:pk>/', views.CommentDetailAPIView.as_view(), name='comment-detail'),
]
