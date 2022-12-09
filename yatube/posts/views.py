from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .constants import SECONDS, STORAGE_TIME
from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post
from .utils import paginator


@cache_page(SECONDS * STORAGE_TIME)
def index(request):
    posts = Post.objects.all()
    template = 'posts/index.html'
    text = "Это главная страница проекта Yatube"
    title = "главная страница проекта Yatube"
    page_obj = paginator(request, posts)
    context = {'posts': posts,
               'text': text,
               'title': title,
               'page_obj': page_obj
               }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.select_related(
        'group'
    )
    page_obj = paginator(request, posts)
    context = {
        'title': group.title,
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(get_user_model(), username=username)
    posts = author.posts.all()
    page_obj = paginator(request, posts)
    posts_count = posts.count()
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=author)
    context = {
        'author': author,
        'page_obj': page_obj,
        'posts_count': posts_count,
        'following': following
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'author': post.author,
        'posts_count': post.author.posts.count(),
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST, files=request.FILES or None,)
    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = request.user
            obj.save()
            return redirect('posts:profile', request.user)
        form = PostForm()
    context = {
        'form': form,
        'is_edit': False
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(request, posts)
    context = {
        'title': 'Follow',
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(get_user_model(), username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(get_user_model(), username=username)
    ).delete()
    return redirect('posts:profile', username)
