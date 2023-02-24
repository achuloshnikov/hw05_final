from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User
from posts.utils import page


def index(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'posts/index.html',
        {
            'page_obj': page(Post.objects.select_related('group'), request),
        },
    )


def group_posts(request: HttpRequest, slug: int) -> HttpResponse:
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('group')
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': page(posts, request),
        },
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    posts_list = author.posts.all()
    if Follow.objects.filter(user=request.user.id).filter(author=author):
        following = True
    else:
        following = False
    return render(
        request,
        'posts/profile.html',
        {
            'author': author,
            'page_obj': page(posts_list, request),
            'following': following,
        },
    )


def post_detail(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST or None)
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': post,
            'form': form,
        },
    )


@login_required
def post_create(request: HttpRequest):
    form = PostForm(request.POST or None)
    if not request.method == 'POST' or not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})

    form.instance.author = request.user
    form.save()

    return redirect('posts:profile', form.instance.author)


@login_required
def post_edit(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('posts:post_detail', pk=pk)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', pk=pk)
    return render(
        request,
        'posts/create_post.html',
        {
            'post': post,
            'form': form,
            'is_edit': True,
        },
    )


@login_required
def add_comment(request: HttpRequest, pk: int):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
    return redirect('posts:post_detail', pk=pk)


@login_required
def follow_index(request: HttpRequest):
    posts = Post.objects.filter(author__following__user=request.user)
    return render(
        request,
        'posts/follow.html',
        {
            'posts': posts,
            'page_obj': page(posts, request),
        },
    )


@login_required
def profile_follow(request: HttpRequest, username: str):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request: HttpRequest, username: str):
    author = get_object_or_404(User, username=username)
    data_follow = request.user.follower.filter(author=author)
    if data_follow.exists():
        data_follow.delete()
    return redirect('posts:profile', username=username)
