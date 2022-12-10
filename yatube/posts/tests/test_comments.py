from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import CommentForm
from posts.models import Post, Comment

User = get_user_model()


class CommentFormAddTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='test post',
        )
        cls.form = CommentForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)

    def test_comments_create(self):
        count_zero = Comment.objects.all().count()
        form_data = {
            'text': 'test 123',
            'post': self.post.id
        }
        self.authorised_client.post(
            reverse('posts:add_comment', kwargs=(
                {'post_id': f'{self.post.id}'})),
            data=form_data,
            follow=True
        )
        count_comment_auth = Comment.objects.all().count()
        self.guest_client.post(
            reverse('posts:add_comment', kwargs=(
                {'post_id': f'{self.post.id}'})),
            data=form_data,
            follow=True
        )
        count_comment_nonauth = Comment.objects.all().count()
        self.assertNotEqual(count_zero, count_comment_auth)
        self.assertEqual(count_comment_nonauth, count_comment_auth)
