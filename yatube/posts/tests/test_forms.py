import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User
from posts.tests.common import image

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateEditFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        auth_user = User.objects.create_user(username='auth')
        auth_user_client = Client()
        auth_user_client.force_login(auth_user)
        test_group = Group.objects.create(
            title='Тест_группа',
            slug='test_group',
            description='test_description',
        )
        data = {
            'group': test_group.id,
            'text': 'Тестовый текст',
            'image': image,
        }
        response = auth_user_client.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': auth_user.username},
            ),
        )
        self.assertEqual(Post.objects.count(), 1)
        new_post = Post.objects.last()
        self.assertEqual(new_post.text, data['text'])
        self.assertEqual(new_post.group.id, data['group'])
        self.assertTrue(Post.objects.filter(image='posts/small.gif').exists)

    def test_edit_post_by_auth(self):
        """Не автор поста, не может внести изменения в пост."""
        auth_user = User.objects.create_user(username='auth')
        auth_user_client = Client()
        auth_user_client.force_login(auth_user)
        test_post = Post.objects.create(
            author=self.author,
            text='Тест_текст',
        )
        auth_user_client.post(
            reverse('posts:post_edit', kwargs={'pk': test_post.pk}),
            data={
                'text': 'Измененный текст',
            },
            follow=True,
        )
        edit_post = Post.objects.get(pk=test_post.pk)
        self.assertEqual(test_post.text, edit_post.text)

    def test_edit_post_by_unauth(self):
        """Неавторизованный пользователь не может внести изменения в пост."""
        test_post = Post.objects.create(
            author=self.author,
            text='Тест_текст',
        )
        self.client.post(
            reverse('posts:post_edit', kwargs={'pk': test_post.pk}),
            data={
                'text': 'Измененный текст',
            },
            follow=True,
        )
        edit_post = Post.objects.get(pk=test_post.pk)
        self.assertEqual(test_post.text, edit_post.text)

    def test_create_post_by_unauth(self):
        """Неавторизованный пользователь не может создать пост."""
        self.client.post(
            reverse('posts:post_create'),
            data={
                'text': 'Тестовый текст',
            },
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_edit_post_by_author(self):
        """Валидная форма редактирует запись в Post."""
        initial_group = Group.objects.create(
            title='Изначальная группа',
            slug='initial_group',
            description='description',
        )
        edit_group = Group.objects.create(
            title='Группа на замену',
            slug='edit_group',
            description='description',
        )
        test_post = Post.objects.create(
            author=self.author,
            group=initial_group,
            text='Тест_текст',
        )
        data = {
            'group': edit_group.id,
            'text': 'Измененный текст',
            'image': image,
        }
        self.author_client.post(
            reverse('posts:post_edit', kwargs={'pk': test_post.pk}),
            data=data,
            follow=True,
        )
        edit_post = Post.objects.get(pk=test_post.pk)
        self.assertEqual(edit_post.group.id, data['group'])
        self.assertEqual(edit_post.text, data['text'])
        self.assertTrue(Post.objects.filter(image='posts/small.gif').exists)

    def test_new_post_following_count(self):
        """Новый пост пояляется для в ленте подписчиков."""
        auth_user = User.objects.create_user(username='auth')
        auth_user_client = Client()
        auth_user_client.force_login(auth_user)
        data = {
            'text': 'Измененный текст',
        }
        self.author_client.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )
        auth_user_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username},
            ),
        )
        self.assertEqual(Post.objects.count(), 1)

    def test_new_post_not_following_count(self):
        """Новый пост не виден в ленте не подписчиков."""
        auth_user = User.objects.create_user(username='auth')
        auth_user_client = Client()
        auth_user_client.force_login(auth_user)
        data = {
            'text': 'Измененный текст',
        }
        self.author_client.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )
        response = auth_user_client.post(
            reverse('posts:follow_index'),
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_create_comment(self):
        """Валидная форма создает комментарий."""
        auth_user = User.objects.create_user(username='auth')
        auth_user_client = Client()
        auth_user_client.force_login(auth_user)
        test_post = Post.objects.create(
            author=self.author,
            text='Тест_текст',
        )
        data = {
            'post': test_post,
            'author': auth_user,
            'text': 'Тестовый комментарий',
        }
        auth_user_client.post(
            reverse('posts:add_comment', kwargs={'pk': test_post.pk}),
            data=data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), 1)
        new_comment = Comment.objects.last()
        self.assertEqual(new_comment.post, data['post'])
        self.assertEqual(new_comment.text, data['text'])
        self.assertEqual(new_comment.author, data['author'])

    def test_create_post_by_unauth(self):
        """Неавторизованный пользователь не может создать комментарий."""
        test_post = Post.objects.create(
            author=self.author,
            text='Тест_текст',
        )
        data = {
            'post': test_post,
            'text': 'Тестовый комментарий',
        }
        self.client.post(
            reverse('posts:add_comment', kwargs={'pk': test_post.pk}),
            data=data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), 0)
