from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        cls.group = Group.objects.create(
            title='Тест_группа',
            slug='test_group',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тест_текст',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def assert_post(self, first_object):
        """Код проверки постов.
        Args:
            first_object: первый видимый пост.
        """
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group.title, self.post.group.title)
        self.assertEqual(first_object.group.pk, self.post.group.pk)
        self.assertEqual(first_object.pk, self.post.pk)
        self.assertEqual(
            first_object.author.username,
            self.post.author.username,
        )
        self.assertEqual(first_object.author.pk, self.post.author.pk)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assert_post(first_object)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
        )
        first_object = response.context['page_obj'][0]
        self.assert_post(first_object)

        self.assertEqual(response.context.get('group').title, self.group.title)
        self.assertEqual(
            response.context.get('group').description,
            self.group.description,
        )
        self.assertEqual(response.context.get('group').slug, self.group.slug)
        self.assertEqual(response.context.get('group').pk, self.group.pk)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user}),
        )
        first_object = response.context['page_obj'][0]
        self.assert_post(first_object)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'pk': self.post.pk}),
        )
        self.assertEqual(response.context.get('post').id, self.post.pk)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'pk': self.post.pk}),
        )
        self.assertEqual(response.context.get('post').id, self.post.pk)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Test_user')
        cls.group = Group.objects.create(
            title='Тест_группа',
            slug='test_group',
            description='test_description',
        )
        for num in range(13):
            Post.objects.create(
                author=cls.user,
                group=cls.group,
                text=f'Тест_текст {num}',
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        list_of_reverses = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for reversing in list_of_reverses:
            response = self.client.get(reversing)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        list_of_reverses = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for reversing in list_of_reverses:
            response = self.client.get(reversing + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)


class PostCreateTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Test_user')
        cls.initial_group = Group.objects.create(
            title='Стартовая группа',
            slug='initial_group',
            description='test_description',
        )
        cls.edit_group = Group.objects.create(
            title='Группа для редактирования',
            slug='edit_group',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.initial_group,
            text='Тест_текст',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_is_visiable(self):
        list_of_reverses = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.initial_group.slug},
            ),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for reversing in list_of_reverses:
            response = self.client.get(reversing)
            self.assertEqual(len(response.context['page_obj']), 1)

    def test_create_post_in_correct_group(self):
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': self.edit_group.slug}),
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class CashTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_index_page_cash(self):
        """Тест кэша главной страницы."""
        author = User.objects.create_user(username='author')
        author_client = Client()
        author_client.force_login(author)
        test_post = Post.objects.create(
            author=author,
            text='Тест_текст',
        )
        response = self.client.get(reverse('posts:index'))
        self.assertContains(response, test_post.text)
        test_post.delete()
        response = self.client.get(reverse('posts:index'))
        self.assertContains(response, test_post.text)
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotContains(response, test_post.text)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.following = User.objects.create_user(username='following')
        cls.following_client = Client()
        cls.following_client.force_login(cls.following)

    def test_follow_unfollow_auth_to_other_auth(self):
        """Авторизованный пользователь может.

        подписаться и отписаться на других пользователей.
        """
        follower = User.objects.create_user(username='follower')
        follower_client = Client()
        follower_client.force_login(follower)
        follower_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.following.username},
            ),
        )
        new_follow = Follow.objects.last()
        self.assertEqual(new_follow.user, follower)
        self.assertEqual(new_follow.author, self.following)
        follower_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.following.username},
            ),
        )
        canceled_follow = Follow.objects.last()
        self.assertIsNone(canceled_follow)

    def test_follow_not_auth(self):
        """Неавторизованный пользователь не может.

        подписаться на других пользователей.
        """
        self.client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.following.username},
            ),
        )
        new_follow = Follow.objects.last()
        self.assertIsNone(new_follow)

    def test_follow_to_myself(self):
        """Пользователь не может подписаться на себя."""
        self.following_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.following.username},
            ),
        )
        new_follow = Follow.objects.last()
        self.assertIsNone(new_follow)

    def test_follow_not_auth_to_not_auth(self):
        """Аноним не может подписаться на анонима."""
        self.client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.client},
            ),
        )
        new_follow = Follow.objects.last()
        self.assertIsNone(new_follow)

    def test_twice_follow_auth_to_other_auth(self):
        """Авторизованный пользователь не может.

        подписаться на другого пользователся несколько раз.
        """
        follower = User.objects.create_user(username='follower')
        follower_client = Client()
        follower_client.force_login(follower)
        follower_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.following.username},
            ),
        )
        follower_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.following.username},
            ),
        )
        new_follows = Follow.objects.all()
        self.assertEqual(new_follows.count(), 1)
