from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post
from yatube.settings import REDUCTION_SYMB_NUM

User = get_user_model()

class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост вапвдодвлопдавопдвоавдопдв',
        )

    def test_model_post_have_correct_object_name(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        self.assertEqual(str(self.post), self.post.text[:REDUCTION_SYMB_NUM])


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_model_group_have_correct_object_name(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        self.assertEqual(str(self.group), self.group.title)
