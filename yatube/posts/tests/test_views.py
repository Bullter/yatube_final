import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='test group',
            slug='test_slug',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test post',
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs=(
                {'slug': f'{self.post.group.slug}'})): 'posts/group_list.html',
            reverse('posts:profile', kwargs=(
                {'username': f'{self.user}'})): 'posts/profile.html',
            reverse('posts:post_detail', kwargs=(
                {'post_id': f'{self.post.id}'})): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs=(
                {'post_id': f'{self.post.id}'})): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorised_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorised_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        contexts = {
            first_object.author.username: 'auth',
            first_object.text: 'test post',
            first_object.group.title: 'test group',
            first_object.image: f'posts/{self.uploaded}'
        }
        for context_value, parametr in contexts.items():
            with self.subTest(context_value=context_value):
                self.assertEqual(context_value, parametr)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorised_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'})
        )
        first_object = response.context['page_obj'][0]
        contexts = {
            first_object.author.username: 'auth',
            first_object.text: 'test post',
            first_object.group.title: 'test group',
            first_object.group.slug: 'test_slug',
            first_object.group.description: 'test description',
            first_object.image: f'posts/{self.uploaded}'
        }
        for context_value, parametr in contexts.items():
            with self.subTest(context_value=context_value):
                self.assertEqual(context_value, parametr)

    def test_cache_index_page(self):
        """ cache the index page"""
        response = self.authorised_client.get(reverse('posts:index'))
        content = response.content
        Post.objects.create(
            text='123',
            group=self.group,
            author=self.user
        )
        response = self.authorised_client.get(reverse('posts:index'))
        content_after_create = response.content
        self.assertEqual(content_after_create, content)
        cache.clear()
        response = self.authorised_client.get(reverse('posts:index'))
        content_after_cache = response.content
        self.assertNotEqual(content_after_cache, content)
