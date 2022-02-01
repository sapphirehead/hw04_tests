from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ADDED_USER = 1
        cls.author = User.objects.create_user(username='UserAndAuthor')
        cls.group = Group.objects.create(
            title='Test title',
            slug=cls.author,
            description='Test description'
        )
        cls.post = Post.objects.create(
            text='Test text1',
            author=cls.author,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(PostFormTests.author)
        self.posts_count = Post.objects.count()

    def test_create_form(self):
        """Валидная форма создает запись в Post."""
        form_data = {
            'text': 'Text text2',
            'author': self.author,
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': self.author}
            )
        )
        self.assertEqual(
            Post.objects.count(), self.posts_count + PostFormTests.ADDED_USER
        )
        self.assertTrue(
            Post.objects.filter(
                text='Text text2',
                author=self.author,
                group=self.group,
            ).exists()
        )

    def test_edit_form(self):
        """Валидная форма редактирует запись в Post."""
        post = Post.objects.get(
            text='Test text1',
            author=self.author,
            group=self.group,
        )
        form_data = {
            'text': 'Test text1 edited',
            'author': self.author,
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': post.id}
            )
        )
        self.assertEqual(Post.objects.count(), self.posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Test text1 edited',
                author=self.author,
                group=self.group,
            ).exists()
        )
