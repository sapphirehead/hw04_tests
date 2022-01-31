from http import HTTPStatus
from django.test import TestCase, Client
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_guest_client_urls_about(self):
        """Возможность перехода анонима на страницы about/"""
        url_names = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK,
        }
        for url, status in url_names.items():
            with self.subTest(url=url, status=status):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_guest_client_urls_uses_correct_template(self):
        """Проверка вызываемых шаблонов для каждого адреса."""
        urls_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, template in urls_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template(self):
        """Namespace соотвествует шаблону."""
        templates_page_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for address, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
