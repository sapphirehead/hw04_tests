from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from ..models import Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Test title',
            slug=cls.author,
            description='Test description',
        )
        cls.post = Post.objects.create(
            text='Test text',
            author=cls.author,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse('posts:group_list', kwargs={'slug': self.group.slug})
             ): 'posts/group_list.html',
            (reverse('posts:profile', kwargs={'username': self.post.author})
             ): 'posts/profile.html',
            (reverse('posts:post_detail', kwargs={'post_id': self.post.id})
             ): 'posts/post_detail.html',
            (reverse('posts:post_edit', kwargs={'post_id': self.post.id})
             ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for address, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_edit_create_pages_show_correct_context(self):
        """Шаблоны create, edit сформированы с правильным контекстом."""
        pages_names = {
            (reverse('posts:post_edit', kwargs={'post_id': self.post.id})
             ): 'form',
            reverse('posts:post_create'): 'form',
        }
        for address, form in pages_names.items():
            response = self.authorized_client_author.get(address)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.models.ModelChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get(form).fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_posts_pages_show_correct_context(self):
        """Шаблоны index, group_list, profile, сформированы
        с правильным контекстом.
        """
        pages_names = {
            reverse('posts:index'): 'page_obj',
            (reverse('posts:group_list', kwargs={'slug': self.group.slug})
             ): 'page_obj',
            (reverse('posts:profile', kwargs={'username': self.author})
             ): 'page_obj',
        }
        for address, form in pages_names.items():
            response = self.authorized_client_author.get(address)
            form_obj_0 = response.context.get(form)[0]
            obj_fields = {
                form_obj_0.author: self.post.author,
                form_obj_0.id: self.post.id,
                form_obj_0.text: self.post.text,
                form_obj_0.pub_date: self.post.pub_date,
                form_obj_0.group.slug: str(self.group.slug)
            }
            for form_value, expected in obj_fields.items():
                with self.subTest(form_value=form_value):
                    self.assertEqual(form_value, expected)

    def test_index_page_list_is_1(self):
        """На страницу со списком постов передаётся
        ожидаемое количество объектов
        """
        response = self.authorized_client_author.get(reverse('posts:index'))
        self.assertEqual(response.context['page_obj'].paginator.count, 1)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом.
        """
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        fields = {
            response.context['post'].id: self.post.id,
            response.context['post'].text: self.post.text,
            response.context['post'].author: self.post.author,
            response.context['post'].group: self.group,
            response.context['post'].pub_date: self.post.pub_date,
        }
        for field, expected in fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_post_with_group_is_on_pages(self):
        """Пост с группой появляется на страницах
        index, post_detail, profile."""
        group_2 = Group.objects.create(
            title='Test title another group',
            slug='AnotherGroup',
            description='Test description another group',
        )
        pages_names = [
            reverse('posts:index'),
            (reverse('posts:group_list', kwargs={'slug': self.group.slug})),
            (reverse('posts:profile', kwargs={'username': self.post.author})),
        ]
        for address in pages_names:
            response = self.authorized_client_author.get(address)
            form_obj_0 = response.context.get('page_obj')[0]
            self.assertEqual(form_obj_0.group.slug, str(self.group.slug))
            self.assertNotEqual(form_obj_0.group.slug, group_2.slug)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.BATCH_SIZE = 13
        cls.author = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Test title',
            slug=cls.author,
            description='Test description',
        )
        cls.posts_list = [
            Post(
                author=cls.author,
                text=f'Текст {i}',
                group=cls.group
            )
            for i in range(cls.BATCH_SIZE)
        ]
        Post.objects.bulk_create(cls.posts_list)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)

    def test__pages_contains_correct_number_records(self):
        """Количество постов на 1-2 странице == 10|3."""
        pages_names = {
            reverse('posts:index'): ['', '?page=2'],
            (reverse('posts:group_list', kwargs={'slug': self.group.slug})
             ): ['', '?page=2'],
            (reverse('posts:profile', kwargs={'username': self.author})
             ): ['', '?page=2'],
        }
        for address, page_list in pages_names.items():
            for i, page in enumerate(page_list):
                with self.subTest(address=address):
                    response = self.guest_client.get(address + page)
                    num = 10 if i == 0 else 3
                    self.assertEqual(
                        response.context['page_obj']
                                .paginator.page(i + 1)
                                .object_list.count(), num)
