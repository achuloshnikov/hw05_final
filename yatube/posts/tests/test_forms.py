import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateEditFormTests(TestCase):
    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        Post.objects.all().delete()
        auth_user = User.objects.create_user(username='auth')
        auth_user_client = Client()
        auth_user_client.force_login(auth_user)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif', content=small_gif, content_type='image/gif'
        )
        test_group = Group.objects.create(
            title='Тест_группа',
            slug='test_group',
            description='test_description',
        )
        data = {
            'group': test_group.id,
            'text': 'Тестовый текст',
            'image': uploaded,
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
        author = User.objects.create_user(username='author')
        author_client = Client()
        author_client.force_login(author)
        test_post = Post.objects.create(
            author=author,
            text='Тест_текст',
        )
        data = {
            'text': 'Измененный текст',
        }
        auth_user_client.post(
            reverse('posts:post_edit', kwargs={'post_id': test_post.pk}),
            data=data,
            follow=True,
        )
        edit_post = Post.objects.get(pk=test_post.pk)
        self.assertEqual(test_post.text, edit_post.text)

    def test_edit_post_by_unauth(self):
        """Неавторизованный пользователь не может внести изменения в пост."""
        author = User.objects.create_user(username='author')
        author_client = Client()
        author_client.force_login(author)
        test_post = Post.objects.create(
            author=author,
            text='Тест_текст',
        )
        data = {
            'text': 'Измененный текст',
        }
        self.client.post(
            reverse('posts:post_edit', kwargs={'post_id': test_post.pk}),
            data=data,
            follow=True,
        )
        edit_post = Post.objects.get(pk=test_post.pk)
        self.assertEqual(test_post.text, edit_post.text)

    def test_create_post_by_unauth(self):
        """Неавторизованный пользователь не может создать пост."""
        data = {
            'text': 'Тестовый текст',
        }
        self.client.post(reverse('posts:post_create'), data=data, follow=True)
        self.assertEqual(Post.objects.count(), 0)

    def test_edit_post_by_author(self):
        """Валидная форма редактирует запись в Post."""
        author = User.objects.create_user(username='author')
        author_client = Client()
        author_client.force_login(author)
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
            author=author,
            group=initial_group,
            text='Тест_текст',
        )
        data = {
            'group': edit_group.id,
            'text': 'Измененный текст',
        }
        author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': test_post.pk}),
            data=data,
            follow=True,
        )
        edit_post = Post.objects.get(pk=test_post.pk)
        self.assertEqual(edit_post.group.id, data['group'])
        self.assertEqual(edit_post.text, data['text'])

    def test_new_post_following_count(self):
        """Новый пост пояляется для в ленте подписчиков"""
        Post.objects.all().delete()
        auth_user = User.objects.create_user(username='auth')
        auth_user_client = Client()
        auth_user_client.force_login(auth_user)
        author = User.objects.create_user(username='author')
        author_client = Client()
        author_client.force_login(author)
        data = {
            'text': 'Измененный текст',
        }
        author_client.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )
        auth_user_client.post(
            reverse(
                'posts:profile_follow', kwargs={'username': author.username}
            ),
        )
        self.assertEqual(Post.objects.count(), 1)

    def test_new_post_following_count(self):
        """Новый пост не виден в ленте не подписчиков"""
        Post.objects.all().delete()
        auth_user = User.objects.create_user(username='auth')
        auth_user_client = Client()
        auth_user_client.force_login(auth_user)
        author = User.objects.create_user(username='author')
        author_client = Client()
        author_client.force_login(author)
        data = {
            'text': 'Измененный текст',
        }
        author_client.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )
        response = auth_user_client.post(
            reverse('posts:follow_index'),
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class CommentFormTests(TestCase):
    def test_create_comment(self):
        """Валидная форма создает комментарий."""
        auth_user = User.objects.create_user(username='auth')
        auth_user_client = Client()
        auth_user_client.force_login(auth_user)
        author = User.objects.create_user(username='author')
        author_client = Client()
        author_client.force_login(author)
        test_post = Post.objects.create(
            author=author,
            text='Тест_текст',
        )
        data = {
            'post': test_post,
            'author': auth_user,
            'text': 'Тестовый комментарий',
        }
        auth_user_client.post(
            reverse('posts:add_comment', kwargs={'post_id': test_post.pk}),
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
        author = User.objects.create_user(username='author')
        author_client = Client()
        author_client.force_login(author)
        test_post = Post.objects.create(
            author=author,
            text='Тест_текст',
        )
        data = {
            'post': test_post,
            'author': self.client,
            'text': 'Тестовый комментарий',
        }
        self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': test_post.pk}),
            data=data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), 0)
