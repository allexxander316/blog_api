from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from blog.models import Post


class TestPostAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='secret')

    def test_get_empty_post(self):
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_get_posts_list(self):
        Post.objects.create(title='Пост 1', content='Содержание поста', author=self.user)
        Post.objects.create(title='Пост 2', content='Содержание поста', author=self.user)

        response = self.client.get('/api/posts/')
        titles = [post['title'] for post in response.data]

        self.assertEqual(len(response.data), 2)
        self.assertIn('Пост 1', titles)
        self.assertIn('Пост 2', titles)

    def test_post_create_authenticated(self):
        data = {
            'title': 'Пост 1',
            'content': 'Содержание поста',
        }
        self.client.login(username='testuser', password='secret')
        response = self.client.post('/api/posts/', data, format='json')

        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], 'Пост 1')

    def test_post_create_unauthenticated(self):
        data = {
            'title': 'Пост 1',
            'content': 'Содержание поста',
        }
        response = self.client.post('/api/posts/', data, format='json')

        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(response.status_code, 403)
        self.assertIn('detail', response.data)

    def test_post_create_invalid_data(self):
        data = {
            'content': 'Содержание поста',
        }
        self.client.login(username='testuser', password='secret')
        response = self.client.post('/api/posts/', data, format='json')

        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.data)
