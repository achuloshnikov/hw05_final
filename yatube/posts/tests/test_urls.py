from http import HTTPStatus

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username='auth_user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тест_группа',
            slug='test_group',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тест_текст',
        )
        cls.auth_user_client = Client()
        cls.author_client = Client()
        cls.auth_user_client.force_login(cls.auth_user)
        cls.author_client.force_login(cls.author)

        cls.urls = {
            'group': reverse('posts:group_list', args=(cls.group.slug,)),
            'index': reverse('posts:index'),
            'post_create': reverse('posts:post_create'),
            'post_detail': reverse(
                'posts:post_detail',
                kwargs={'pk': cls.post.pk},
            ),
            'post_edit': reverse(
                'posts:post_edit',
                kwargs={'pk': cls.post.pk},
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': cls.post.author.get_username()},
            ),
            'add_comment': reverse(
                'posts:add_comment',
                kwargs={'pk': cls.post.pk},
            ),
            'follow_index': reverse('posts:follow_index'),
            'profile_follow': reverse(
                'posts:profile_follow',
                kwargs={'username': cls.author.username}
            ),
             'profile_unfollow': reverse(
                'posts:profile_unfollow',
                kwargs={'username': cls.author.username}
            ),
            'missing': ('something/really/weird/'),
        }

    def test_http_statuses(self) -> None:
        httpstatuses = (
            (self.urls.get('group'), HTTPStatus.OK, self.client),
            (self.urls.get('index'), HTTPStatus.OK, self.client),
            (self.urls.get('post_detail'), HTTPStatus.OK, self.client),
            (self.urls.get('profile'), HTTPStatus.OK, self.client),
            (self.urls.get('post_create'), HTTPStatus.FOUND, self.client),
            (
                self.urls.get('post_create'),
                HTTPStatus.OK,
                self.auth_user_client,
            ),
            (self.urls.get('post_edit'), HTTPStatus.FOUND, self.client),
            (
                self.urls.get('post_edit'),
                HTTPStatus.FOUND,
                self.auth_user_client,
            ),
            (self.urls.get('post_edit'), HTTPStatus.OK, self.author_client),
            (self.urls.get('add_comment'), HTTPStatus.FOUND, self.client),
            (self.urls.get('follow_index'), HTTPStatus.FOUND, self.client),
            (self.urls.get('follow_index'), HTTPStatus.OK, self.auth_user_client),
            (self.urls.get('profile_follow'), HTTPStatus.FOUND, self.client),
            (self.urls.get('profile_follow'), HTTPStatus.FOUND, self.author_client),
            (self.urls.get('profile_unfollow'), HTTPStatus.FOUND, self.client),
            (self.urls.get('profile_unfollow'), HTTPStatus.FOUND, self.author_client),
            (self.urls.get('missing'), HTTPStatus.NOT_FOUND, self.client),
        )
        for url, status, user in httpstatuses:
            with self.subTest(url=url, status=status, user=user):
                self.assertEqual(user.get(url).status_code, status)

    def test_templates(self) -> None:
        templates = (
            (
                self.urls.get('group'),
                'posts/group_list.html',
                self.author_client,
            ),
            (self.urls.get('index'), 'posts/index.html', self.author_client),
            (
                self.urls.get('post_detail'),
                'posts/post_detail.html',
                self.author_client,
            ),
            (
                self.urls.get('profile'),
                'posts/profile.html',
                self.author_client,
            ),
            (
                self.urls.get('post_create'),
                'posts/create_post.html',
                self.author_client,
            ),
            (
                self.urls.get('post_edit'),
                'posts/create_post.html',
                self.author_client,
            ),
        )
        for url, template, user in templates:
            with self.subTest(url=url):
                self.assertTemplateUsed(user.get(url), template)

    def test_redirects(self) -> None:
        redirects = (
            (
                self.urls.get('post_create'),
                (
                    f"{reverse('users:login')}?next="
                    f"{self.urls.get('post_create')}"
                ),
                self.client,
            ),
            (
                self.urls.get('post_edit'),
                f"{reverse('users:login')}?next={self.urls.get('post_edit')}",
                self.client,
            ),
            (
                self.urls.get('post_edit'),
                self.urls.get('post_detail'),
                self.auth_user_client,
            ),
        )
        for url, redirect_url, user in redirects:
            with self.subTest(url=url):
                self.assertRedirects(user.get(url), redirect_url)
