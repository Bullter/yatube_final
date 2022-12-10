from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test group',
            slug='test_slug',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)
        cache.clear()

    def test_urls_uses_correct_template(self):
        templates_url_names = {'/': 'posts/index.html'}
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorised_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_redirect_not_auth_client(self):
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)

    def test_404_url(self):
        response = self.authorised_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
