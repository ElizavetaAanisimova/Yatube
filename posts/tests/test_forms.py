import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

        cls.form = PostForm()

        cls.user = User.objects.create(
            username='TestName',
            email='Test@yandex.ru',
            password='test01'
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_new_post(self):
        """Создание поста прошло успешно."""
        posts_count = Post.objects.count()
        form_data = {
            'group': PostFormTests.group.id,
            'text': 'необычный Тестовый пост',
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))

        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_new_post_with_image(self):
        """Создание поста с картинкой прошло успешно."""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=PostFormTests.small_gif,
            content_type='image/gif'
        )

        form_data = {
            'group': PostFormTests.group.id,
            'text': 'Тестовый пост',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=PostFormTests.group.id,
                text='Тестовый пост',
                image='posts/small.gif',
            ).exists()
        )

    def test_edit_post(self):
        """Редактирование поста прошло успешно."""
        new_form_data = {
            'group': PostFormTests.group.id,
            'text': 'Другой тестовый пост'
        }
        response = self.authorized_client.post(reverse(
            'post_edit',
            kwargs={
                'username': PostFormTests.user.username,
                'post_id': PostFormTests.post.id
            }),
            data=new_form_data,
            follow=True
        )
        self.post.refresh_from_db()
        self.assertEqual(
            response.context['user_post'].text, new_form_data['text']
        )

    def test_profile_check_context_contains_image(self):
        """Изображение передаётся в словаре context на страницу профайла"""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user.username})
        )
        self.assertTrue(response.context['page'][0].image)

    def test_index_check_context_contains_image(self):
        """Изображение передаётся в словаре context на главную страницу"""
        response = self.authorized_client.get(reverse('index'))
        self.assertTrue(response.context['page'][0].image)

    def test_group_check_context_contains_image(self):
        """Изображение передаётся в словаре context на страницу группы"""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.group.slug})
        )
        self.assertTrue(response.context['page'][0].image)

    def test_post_check_context_contains_image(self):
        """Изображение передаётся в словаре context на страницу поста"""
        response = self.authorized_client.get(
            reverse('post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            })
        )
        self.assertTrue(response.context['user_post'].image)
