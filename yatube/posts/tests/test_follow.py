from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Group, Post

User = get_user_model()


class FollowViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test group',
            slug='test_slug',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='test post',
            group=cls.group,
        )

    def setUp(self):
        self.user = User.objects.create_user(username='qwerty')
        self.person = User.objects.create_user(username='qwertyh')
        self.authorised_client = Client()
        self.unfollow_client = Client()
        self.authorised_client.force_login(self.user)
        self.unfollow_client.force_login(self.person)
        cache.clear()

    def test_follow_function(self):
        """Проверка подписки и отписки"""
        self.authorised_client.get(reverse(
            'posts:profile_follow',
            kwargs=({'username': self.author.username})))
        subscriptions = Follow.objects.filter(user=self.user, author=self.author)
        self.assertTrue(bool(subscriptions))
        self.authorised_client.get(reverse(
            'posts:profile_unfollow',
            kwargs=({'username': self.author.username})))
        subscriptions = Follow.objects.filter(user=self.user, author=self.author)
        self.assertFalse(bool(subscriptions))

    def test_post_visibility(self):
        """тест на видимость постов автора,
        дедлайн близко так, что
        'вперед и в продакшен'"""
        self.authorised_client.get(reverse(
            'posts:profile_follow',
            kwargs=({'username': self.author.username})))
        Post.objects.create(
            author=self.author,
            text='123123',
            group=self.group,
        )
        response_follow = self.authorised_client.get(reverse('posts:follow_index'))
        response_unfollow = self.unfollow_client.get(reverse('posts:follow_index'))
        self.assertNotEqual(response_follow, response_unfollow)
