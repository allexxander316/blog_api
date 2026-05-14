from django.contrib.auth import get_user_model
from django.test import TestCase

from blog.serializers import PostSerializer, CommentSerializer

from blog.models import Post, Comment


class TestPostSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser', password='secret')

    def setUp(self):
        self.valid_data = {
            'title': 'Заголовок',
            'content': 'Содержание поста',
        }

    def test_serializer_valid_data(self):
        serializer = PostSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_creates_post(self):
        serializer = PostSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        post = serializer.save(author=self.user)

        self.assertIsNotNone(post.pk)
        self.assertEqual(post.title, 'Заголовок')
        self.assertEqual(post.author, self.user)

    def test_serializer_missing_title(self):
        invalid_data = {
            'content': 'Содержание поста',
        }
        serializer = PostSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_serializer_output_format(self):
        post = Post.objects.create(title='Заголовок', content='Контент', author=self.user)
        serializer = PostSerializer(post)
        data = serializer.data

        self.assertIn('title', data)
        self.assertIn('content', data)
        self.assertEqual(data['title'], 'Заголовок')


class TestCommentSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser', password='secret')
        cls.post = Post.objects.create(title='Заголовок', content='Содержание поста', author=cls.user)

    def setUp(self):
        self.valid_data = {'content': 'Содержание комментария'}

    def test_serializer_valid_data(self):
        serializer = CommentSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_creates_comment(self):
        serializer = CommentSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        comment = serializer.save(author=self.user, post=self.post)
        self.assertIsNotNone(comment.pk)
        self.assertEqual(comment.content, 'Содержание комментария')
        self.assertEqual(Comment.objects.count(), 1)

    def test_serializer_missing_content(self):
        invalid_data = {}
        serializer = CommentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('content', serializer.errors)

    def test_serializer_output_format(self):
        comment = Comment.objects.create(content='Содержание комментария', author=self.user, post=self.post)
        serializer = CommentSerializer(comment)
        data = serializer.data

        self.assertIn('content', data)
        self.assertEqual(data['content'], 'Содержание комментария')
