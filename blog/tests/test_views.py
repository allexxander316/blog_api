from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from blog.models import Post, Comment


class TestPostAPI(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.anonymous_client = APIClient()
        cls.user = get_user_model().objects.create_user(username='testuser', password='secret')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_empty_post(self):
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_get_posts_list(self):
        Post.objects.create(title='Пост 1', content='Содержание поста', author=self.user)
        Post.objects.create(title='Пост 2', content='Содержание поста', author=self.user)

        response = self.client.get(reverse('post-list'))
        titles = [post['title'] for post in response.data]

        self.assertEqual(len(response.data), 2)
        self.assertIn('Пост 1', titles)
        self.assertIn('Пост 2', titles)

    def test_post_create_authenticated(self):
        data = {
            'title': 'Пост 1',
            'content': 'Содержание поста',
        }
        response = self.client.post(reverse('post-list'), data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(response.data['title'], 'Пост 1')

    def test_post_create_unauthenticated(self):
        data = {
            'title': 'Пост 1',
            'content': 'Содержание поста',
        }
        response = self.anonymous_client.post(reverse('post-list'), data, format='json')

        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(response.status_code, 401)
        self.assertIn('detail', response.data)

    def test_post_create_invalid_data(self):
        data = {
            'content': 'Содержание поста',
        }
        response = self.client.post(reverse('post-list'), data, format='json')

        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.data)


class TestPostDetailView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser', password='secret')
        cls.anonymous_client = APIClient()

    def setUp(self):
        self.post = Post.objects.create(title='Заголовок', content='Содержимое поста', author=self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_post_detail(self):
        response = self.client.get(reverse('post-detail', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Заголовок')

    def test_author_can_update_own_post_title(self):
        data = {'title': 'Новый заголовок', 'content': 'Содержимое поста'}
        response = self.client.put(reverse('post-detail', kwargs={'pk': self.post.pk}), data, format='json')

        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Новый заголовок')
        self.assertEqual(response.data['title'], 'Новый заголовок')

    def test_anonymous_cannot_update_post(self):
        data = {'title': 'Новый заголовок', 'content': 'Содержимое поста'}
        response = self.anonymous_client.put(reverse('post-detail', kwargs={'pk': self.post.pk}), data, format='json')

        self.assertEqual(response.status_code, 401)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Заголовок')

    def test_non_author_cannot_update_post(self):
        other_user = get_user_model().objects.create_user(username='otheruser', password='secret')
        data = {'title': 'Новый заголовок', 'content': 'Содержимое поста'}
        self.client.force_authenticate(user=other_user)
        response = self.client.put(reverse('post-detail', kwargs={'pk': self.post.pk}), data, format='json')

        self.assertEqual(response.status_code, 403)
        self.post.refresh_from_db()
        self.assertNotEqual(self.post.title, data['title'])

    def test_author_can_delete_own_post(self):
        response = self.client.delete(reverse('post-detail', kwargs={'pk': self.post.pk}))
        posts = Post.objects.count()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(posts, 0)

    def test_anonymous_cannot_delete_post(self):
        response = self.anonymous_client.delete(reverse('post-detail', kwargs={'pk': self.post.pk}))

        posts = Post.objects.count()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(posts, 1)

    def test_non_author_cannot_delete_post(self):
        other_user = get_user_model().objects.create_user(username='otheruser', password='secret')
        self.client.force_authenticate(user=other_user)
        response = self.client.delete(reverse('post-detail', kwargs={'pk': self.post.pk}))

        self.assertEqual(response.status_code, 403)

    def test_nonexistent_post(self):
        response = self.client.get(reverse('post-detail', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)


class TestCommentAPI(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser', password='secret')
        cls.post = Post.objects.create(title='Заголовок', content='Содержимое поста', author=cls.user)
        cls.anonymous_client = APIClient()

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_empty_comments(self):
        response = self.client.get(reverse('comment-list', kwargs={'post_pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_get_comments_list(self):
        Comment.objects.create(content='Содержимое комментария', author=self.user, post=self.post)
        Comment.objects.create(content='Содержимое комментария 2', author=self.user, post=self.post)

        response = self.client.get(reverse('comment-list', kwargs={'post_pk': self.post.pk}))
        comments = [comment['content'] for comment in response.data]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertIn('Содержимое комментария', comments)
        self.assertIn('Содержимое комментария 2', comments)

    def test_post_create_comment_authenticated(self):
        data = {'content': 'Новый комментарий'}
        response = self.client.post(reverse('comment-list', kwargs={'post_pk': self.post.pk}), data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual('Новый комментарий', response.data['content'])

    def test_anonymous_cant_create_comment(self):
        data = {'content': 'Новый комментарий'}
        response = self.anonymous_client.post(reverse('comment-list', kwargs={'post_pk': self.post.pk}), data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Comment.objects.count(), 0)
        self.assertIn('detail', response.data)

    def test_post_create_comment_invalid_data(self):
        data = {}
        response = self.client.post(reverse('comment-list', kwargs={'post_pk': self.post.pk}), data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Comment.objects.count(), 0)
        self.assertIn('content', response.data)


class TestCommentDetailAPI(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser', password='secret')
        cls.post = Post.objects.create(title='Заголовок', content='Содержимое поста', author=cls.user)

    def setUp(self):
        self.comment = Comment.objects.create(content='Содержимое комментария', author=self.user, post=self.post)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_comment_detail(self):
        response = self.client.get(reverse('comment-detail', kwargs={'pk': self.comment.pk,
                                                                     'post_pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['content'], self.comment.content)

    def test_author_can_update_comment(self):
        data = {'content': 'Новое содержимое комментария'}
        response = self.client.put(reverse('comment-detail', kwargs={'pk': self.comment.pk,
                                                                     'post_pk': self.post.pk}), data)
        self.comment.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.comment.content, data['content'])
        self.assertEqual(self.comment.author, self.user)

    def test_update_comment_invalid(self):
        data = {}
        response = self.client.put(reverse('comment-detail', kwargs={'pk': self.comment.pk,
                                                                     'post_pk': self.post.pk}), data)
        self.comment.refresh_from_db()
        self.assertEqual(response.status_code, 400)

    def test_non_author_cannot_update_comment(self):
        other_user = get_user_model().objects.create_user(username='otheruser', password='secret')
        self.client.force_authenticate(user=other_user)
        data = {'content': 'Новое содержимое комментария'}
        response = self.client.put(reverse('comment-detail', kwargs={'pk': self.comment.pk,
                                                                     'post_pk': self.post.pk}))
        self.comment.refresh_from_db()

        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(self.comment.content, data['content'])
        self.assertIn('detail', response.data)

    def test_author_can_delete_comment(self):
        response = self.client.delete(reverse('comment-detail', kwargs={'pk': self.comment.pk,
                                                                        'post_pk': self.post.pk}))
        comments = Comment.objects.count()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(comments, 0)

    def test_non_author_cannot_delete_comment(self):
        other_user = get_user_model().objects.create(username='otheruser', password='secret')
        self.client.force_authenticate(user=other_user)
        response = self.client.delete(reverse('comment-detail', kwargs={'pk': self.comment.pk,
                                                                        'post_pk': self.post.pk}))

        comments = Comment.objects.count()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(comments, 1)

    def test_get_nonexistent_comment(self):
        response = self.client.get(reverse('comment-detail', kwargs={'pk': 999, 'post_pk': self.post.pk}))

        self.assertEqual(response.status_code, 404)
