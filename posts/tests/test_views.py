from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(
            username='TestName',
            email='Test@yandex.ru',
            password='test01'
        )

        cls.user1 = get_user_model().objects.create(
            username='TestName1',
            email='Test1@yandex.ru',
            password='test001'
        )

        cls.user2 = get_user_model().objects.create(
            username='TestName2',
            email='Test2@yandex.ru',
            password='test002'
        )

        cls.following = Follow.objects.get_or_create(
            user=cls.user1, author=cls.user
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )

        cls.group1 = Group.objects.create(
            title='Тестовая группа1',
            slug='test-slug1',
            description='Тестовое описание1'
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostPagesTests.user
        self.authorized_client = Client()
        self.authorized_client1 = Client()
        self.authorized_client2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client1.force_login(self.user1)
        self.authorized_client2.force_login(self.user2)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse(
                'group_posts', kwargs={'slug': 'test-slug'}
            ),
            'new.html': reverse('new_post'),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом
        и содержит созданный пост."""
        response = self.guest_client.get(reverse('index'))
        post_object = response.context['page'][0]
        post_author = post_object.author
        post_text = post_object.text
        post_pub_date = post_object.pub_date
        self.assertEqual(post_author, PostPagesTests.user)
        self.assertEqual(post_text, PostPagesTests.post.text)
        self.assertEqual(post_pub_date, PostPagesTests.post.pub_date)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(
            response.context['group'].title, PostPagesTests.group.title
        )
        self.assertEqual(
            response.context['group'].description,
            PostPagesTests.group.description
        )
        self.assertEqual(
            response.context['group'].slug, PostPagesTests.group.slug
        )

    def test_new_post_in_group(self):
        """Пост сохраняется в группе."""
        posts_count = Post.objects.filter(group=PostPagesTests.group).count()
        Post.objects.create(
            text='Тестовый текст для нового поста',
            author=PostPagesTests.user,
            group=PostPagesTests.group,
        )
        self.assertNotEqual(Post.objects.filter(
            group=PostPagesTests.group).count(), posts_count
        )

    def test_new_post_not_in_another_group(self):
        """Пост не сохраняется в группе, не предназначенной для него."""
        posts_count = Post.objects.filter(group=PostPagesTests.group1).count()
        Post.objects.create(
            text='Тестовый текст для нового поста',
            author=PostPagesTests.user,
            group=PostPagesTests.group,
        )
        self.assertEqual(Post.objects.filter(
            group=PostPagesTests.group1).count(), posts_count
        )

    def test_new_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_correct_context(self):
        """Шаблон new для edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'post_edit', kwargs={
                'username': PostPagesTests.user.username,
                'post_id': PostPagesTests.post.id
            })
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse(
            'profile', kwargs={'username': PostPagesTests.user.username})
        )
        post_object = response.context['page'][0]
        post_username = post_object.author.username
        post_text = post_object.text
        post_pub_date = post_object.pub_date
        self.assertEqual(post_username, PostPagesTests.user.username)
        self.assertEqual(post_text, PostPagesTests.post.text)
        self.assertEqual(post_pub_date, PostPagesTests.post.pub_date)

    def test_post_pages_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'post', kwargs={
                    'username': PostPagesTests.user.username,
                    'post_id': PostPagesTests.post.id
                })
        )
        self.assertEqual(
            response.context['user_post'].text, PostPagesTests.post.text
        )
        self.assertEqual(
            response.context['user_post'].author.username,
            PostPagesTests.user.username
        )
        self.assertEqual(response.context['user_post'], PostPagesTests.post)

    def test_index_page_cache(self):
        """Записи Index хранятся в кэше и обновлялся раз в 20 секунд"""
        response_1 = self.authorized_client.get(reverse('index'))
        Post.objects.create(
            text='Тестовый текст для кэша',
            author=PostPagesTests.user,
            group=PostPagesTests.group,
        )
        response_2 = self.authorized_client.get(reverse('index'))
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('index'))
        self.assertNotEqual(response_2.content, response_3.content)

    def test_following_authorized_client(self):
        """Авторизованный пользователь может подписаться"""
        self.assertTrue(Follow.objects.filter(
            user=PostPagesTests.user1,
            author=PostPagesTests.user).exists())

    def test_unfollowing_authorized_client(self):
        """Авторизованный пользователь может отписаться"""
        Follow.objects.filter(
            user=PostPagesTests.user1,
            author=PostPagesTests.user).delete()
        self.assertFalse(Follow.objects.filter(
            user=PostPagesTests.user1,
            author=PostPagesTests.user).exists())

    def test_new_post_in_following_page(self):
        """Пост появляется в ленте у тех, кто подписан."""
        response = self.authorized_client1.get(reverse('follow_index'))
        post_count = len(response.context.get('page').object_list)
        Post.objects.create(
            text='Тестовый текст для нового поста',
            author=PostPagesTests.user,
            group=PostPagesTests.group,
        )
        response = self.authorized_client1.get(reverse('follow_index'))
        post_count1 = len(response.context.get('page').object_list)
        self.assertEqual(post_count + 1, post_count1)

    def test_new_post_not_in_following_page(self):
        """Пост не появляется в ленте у тех, кто не подписан."""
        response = self.authorized_client2.get(reverse('follow_index'))
        post_count = len(response.context.get('page').object_list)
        Post.objects.create(
            text='Тестовый текст для нового поста',
            author=PostPagesTests.user,
            group=PostPagesTests.group,
        )
        response = self.authorized_client2.get(reverse('follow_index'))
        post_count1 = len(response.context.get('page').object_list)
        self.assertEqual(post_count, post_count1)
