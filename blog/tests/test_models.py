from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from blog.models import Post

class TestPostModel(TestCase):
    def test_create_post(self):
        user = get_user_model().objects.create_user(username='testuser', password='secret')
        post = Post.objects.create(title="Пост", content='Контент', author=user)

        self.assertIsNotNone(post.pk)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post.title, 'Пост')
        self.assertEqual(post.content, 'Контент')
        self.assertEqual(post.author, user)
        self.assertFalse(post.is_published)

    def test_str_returns_title(self):
        user = get_user_model().objects.create_user(username='testuser', password='secret')
        post = Post.objects.create(title="Пост", content='Контент', author=user)

        self.assertEqual(str(post), post.title)

    def test_publish_sets_is_published_true(self):
        user = get_user_model().objects.create_user(username='testuser', password='secret')
        post = Post.objects.create(title="Пост", content='Контент', author=user)

        post.publish()
        post.refresh_from_db()

        self.assertTrue(post.is_published)

    def test_unpublish_sets_is_published_false(self):
        user = get_user_model().objects.create_user(username='testuser', password='secret')
        post = Post.objects.create(title="Пост", content='Контент', author=user)

        post.unpublish()
        post.refresh_from_db()

        self.assertFalse(post.is_published)

    def test_auto_timestamps(self):
        user = get_user_model().objects.create_user(username='testuser', password='secret')
        post = Post.objects.create(title="Пост", content='Контент', author=user)

        self.assertIsInstance(post.created_at, datetime)
        self.assertIsInstance(post.updated_at, datetime)