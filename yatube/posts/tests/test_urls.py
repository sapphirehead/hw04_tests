from http import HTTPStatus
from django.test import TestCase, Client
from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_is_author = User.objects.create_user(username='IsAuthor')
        cls.user_is_not_author = User.objects.create_user(
            username='IsNotAuthor'
        )

        cls.group = Group.objects.create(
            title='Test1',
            slug=cls.user_is_author,
            description='Test description',
        )
        cls.test_post = Post.objects.create(
            author=cls.user_is_author,
            text='Test text',
            group=cls.group
        )
        cls.urls_statuses = {
            '/': HTTPStatus.OK,
            f'/group/{cls.user_is_author}/': HTTPStatus.OK,
            f'/profile/{cls.user_is_not_author}/': HTTPStatus.OK,
            f'/profile/{cls.user_is_author}/': HTTPStatus.OK,
            f'/posts/{cls.test_post.id}/': HTTPStatus.OK,
            '/unexpected/': HTTPStatus.NOT_FOUND,
        }
        cls.urls_templates = {
            '/': 'posts/index.html',
            f'/group/{cls.user_is_author}/': 'posts/group_list.html',
            f'/posts/{cls.test_post.id}/': 'posts/post_detail.html',
            f'/profile/{cls.user_is_author}/': 'posts/profile.html',
            f'/posts/{cls.test_post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        cls.urls_redirects = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{cls.test_post.id}/edit/':
                f'/auth/login/?next=/posts/{cls.test_post.id}/edit/',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_not_author = Client()
        self.authorized_client_author.force_login(
            PostURLTests.user_is_author)
        self.authorized_client_not_author.force_login(
            PostURLTests.user_is_not_author)

    def test_url_exists_at_desired_location(self):
        """index, profile, posts/id доступны любому пользователю."""
        for url, status in PostURLTests.urls_statuses.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю.
        """
        response = self.authorized_client_not_author.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_exists_at_desired_location_authorized(self):
        """Страница /posts/post_id/edit/ доступна автору."""
        response = self.authorized_client_author.get(
            f'/posts/{PostURLTests.test_post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous_on_auth_login(self):
        """Попытка создания/редактирования поста анонимом,
        страница перенаправит на страницу логина.
        """
        for url, redirect_url in PostURLTests.urls_redirects.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect_url)

    def test_user_not_author_cannot_edit_post(self):
        """Попытка редактирования поста неавтором, страница
        перенаправит на страницу поста.
        """
        response = self.authorized_client_not_author.get(
            f'/posts/{PostURLTests.test_post.id}/edit/'
        )
        self.assertRedirects(
            response, f'/posts/{PostURLTests.test_post.id}/'
        )

    def test_urls_uses_correct_template(self):
        """Проверка вызываемых шаблонов для каждого адреса"""
        for url, template in PostURLTests.urls_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client_author.get(url)
                self.assertTemplateUsed(response, template)
