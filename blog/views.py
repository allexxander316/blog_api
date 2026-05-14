from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from blog.models import Post, Comment
from blog.serializers import PostSerializer, CommentSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        # post = Post.objects.get(pk=self.kwargs.get('pk'))
        instance = self.get_object()
        if instance.author == request.user:
            return super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author == request.user:
            return super().destroy(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return []
        return [IsAuthenticated()]


class CommentAPIView(APIView):
    def get(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, post_pk):
        serializer = CommentSerializer(data=request.data)
        post = get_object_or_404(Post, pk=post_pk)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []


class CommentDetailAPIView(APIView):
    def get(self, request, pk, post_pk):
        comment = get_object_or_404(Comment, pk=pk, post_id=post_pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, pk, post_pk):
        comment = get_object_or_404(Comment, pk=pk, post_id=post_pk)
        if comment.author != request.user:
            return Response({"detail": 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CommentSerializer(instance=comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, post_pk):
        comment = get_object_or_404(Comment, pk=pk, post_id=post_pk)
        if comment.author != request.user:
            return Response({"detail": 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.request.method in ('PUT', 'DELETE'):
            return [IsAuthenticated()]
        return []