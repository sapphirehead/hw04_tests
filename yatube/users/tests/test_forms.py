from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class UserFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_reverse_signup_create_new_user(self):
        """при заполнении формы reverse('users:signup')
        создаётся новый пользователь.
        """
        users_count = User.objects.count()
        form_data = {
            'first_name': 'UserFistName',
            'last_name': 'UserLastName',
            'username': 'NewUser',
            'email': 'l@l.ru',
            'password1': '1111111p',
            'password2': '1111111p',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                username='NewUser',
            ).exists()
        )
