from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.OK = HTTPStatus.OK.value
        cls.NOT_FOUND = HTTPStatus.NOT_FOUND.value
        cls.user_is_author = User.objects.create_user(username='IsAuthor')
        cls.user_is_not_author = User.objects.create_user(
            username='IsNotAuthor'
        )

        cls.not_author = str(cls.user_is_not_author)
        cls.author = str(cls.user_is_author)
        cls.group = Group.objects.create(
            title='Test1',
            slug=cls.author,
            description='Test description',
        )
        cls.test_post = Post.objects.create(
            author=cls.user_is_author,
            text='Test text',
            group=cls.group
        )
        cls.post_id = str(cls.test_post.id)

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
        urls_names = {
            '/': self.OK,
            f'/group/{self.author}/': self.OK,
            f'/profile/{self.not_author}/': self.OK,
            f'/profile/{self.author}/': self.OK,
            f'/posts/{self.post_id}/': self.OK,
            '/unexpected/': self.NOT_FOUND,
        }
        for url, status in urls_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю.
        """
        response = self.authorized_client_not_author.get('/create/')
        self.assertEqual(response.status_code, self.OK)

    def test_post_edit_url_exists_at_desired_location_authorized(self):
        """Страница /posts/post_id/edit/ доступна автору."""
        response = self.authorized_client_author.get(
            '/posts/' + self.post_id + '/edit/'
        )
        self.assertEqual(response.status_code, self.OK)

    def test_urls_redirect_anonymous_on_auth_login(self):
        """Попытка создания/редактирования поста анонимом,
        страница перенаправит на страницу логина.
        """
        urls_names = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post_id}/edit/':
                f'/auth/login/?next=/posts/{self.post_id}/edit/',
        }
        for url, redirect_url in urls_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect_url)

    def test_user_not_author_edit_post(self):
        """Попытка редактирования поста неавтором, страница
        перенаправит на страницу поста.
        """
        response = self.authorized_client_not_author.get(
            f'/posts/{self.post_id}/edit/')
        self.assertRedirects(response, f'/posts/{self.post_id}/')

    def test_urls_uses_correct_template(self):
        """Проверка вызываемых шаблонов для каждого адреса"""
        url_names = {
            '/': 'posts/index.html',
            f'/group/{self.author}/': 'posts/group_list.html',
            f'/posts/{self.post_id}/': 'posts/post_detail.html',
            f'/profile/{self.author}/': 'posts/profile.html',
            f'/posts/{self.post_id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client_author.get(url)
                self.assertTemplateUsed(response, template)
