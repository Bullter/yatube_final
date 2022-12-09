from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.constants import POSTS_PER_PAGE, SECOND_PAGE, TOTAL_POSTS
from posts.models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test group',
            slug='test-slug',
            description='test description',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)
        context_posts: list = []
        for i in range(TOTAL_POSTS):
            context_posts.append(Post(
                text=f'test text {i}',
                group=self.group,
                author=self.user
            ))
        Post.objects.bulk_create(context_posts)

    def test_paginator(self):
        reverse_name_posts = {
            reverse('posts:index'): POSTS_PER_PAGE,
            reverse('posts:index') + '?page=2': SECOND_PAGE,
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}): POSTS_PER_PAGE,
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}) + '?page=2': SECOND_PAGE,
            reverse('posts:profile',
                    kwargs={'username': 'auth'}): POSTS_PER_PAGE,
            reverse('posts:profile',
                    kwargs={'username': 'auth'}) + '?page=2': SECOND_PAGE,
        }
        for reverse_name, posts in reverse_name_posts.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorised_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), posts)
