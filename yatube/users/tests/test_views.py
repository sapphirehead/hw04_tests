from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_client = User.objects.create_user(username='TestUser')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author_client)

    def test_urls_of_authorized_uses_correct_template(self):
        """URL-адрес от authorized использует соответствующий шаблон."""
        addresses = {
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_confirm',
                    kwargs={'uidb64': 'uidb64', 'token': 'token'}):
                'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
        }
        for address, template in addresses.items():
            with self.subTest(address=address, template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_authorized_client_change_correct_template(self):
        """Проверка вызываемых шаблонов для изменения пароля"""
        templates_url_names = {
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url, template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_of_anonymous_uses_correct_template(self):
        """URL-адрес от анонима использует соответствующий шаблон.
        """
        addresses = {
            reverse('users:login'): 'users/login.html',
            reverse('users:signup'): 'users/signup.html',
        }
        for address, template in addresses.items():
            with self.subTest(address=address, template=template):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_users_signup_show_correct_context(self):
        """в контексте передаётся форма для создания нового
        пользователя.
        """
        response = self.guest_client.get(reverse('users:signup'))
        form_obj = response.context.get('form')
        self.assertIsNotNone(form_obj)
