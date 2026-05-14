from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from blog.models import Post, Comment


class TestPostModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser', password='secret')

    def setUp(self):
        self.post = Post.objects.create(title="Пост", content='Контент', author=self.user)

    def test_create_post(self):
        self.assertIsNotNone(self.post.pk)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(self.post.title, 'Пост')
        self.assertEqual(self.post.content, 'Контент')
        self.assertEqual(self.post.author, self.user)
        self.assertFalse(self.post.is_published)

    def test_str_returns_title(self):
        self.assertEqual(str(self.post), self.post.title)

    def test_publish_sets_is_published_true(self):
        self.post.publish()
        self.post.refresh_from_db()

        self.assertTrue(self.post.is_published)

    def test_unpublish_sets_is_published_false(self):
        self.post.unpublish()
        self.post.refresh_from_db()

        self.assertFalse(self.post.is_published)

    def test_auto_timestamps(self):
        self.assertIsInstance(self.post.created_at, datetime)
        self.assertIsInstance(self.post.updated_at, datetime)


class TestCommentModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser', password='secret')
        cls.post = Post.objects.create(title="Пост", content='Контент', author=cls.user)

    def setUp(self):
        self.comment = Comment.objects.create(post=self.post, author=self.user,
                                              content='Контент')

    def test_create_comment(self):
        self.assertIsNotNone(self.comment.pk)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.comment.content, 'Контент')
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.post, self.post)

    def test_str_returns_content_preview(self):
        self.assertEqual(str(self.comment), 'Контент')

    def test_str_appends_ellipsis_for_long_content(self):
        long_content = ('Спасибо за отличную статью! Очень помогла разобраться'
                        ' в сложной теме, теперь буду рекомендовать друзьям.')

        self.assertGreater(len(long_content), 50)
        comment = Comment.objects.create(author=self.user, post=self.post, content=long_content)
        expected = long_content[:50] + '...'

        self.assertEqual(str(comment), expected)

    def test_comment_belongs_to_post(self):
        self.assertEqual(self.comment.post, self.post)
