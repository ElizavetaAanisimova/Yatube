from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(
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
            group=cls.group
        )

        cls.guest_client = Client()

        for i in range(12):
            Post.objects.create(
                text='Тестовый пост',
                author=PaginatorViewsTest.user,
                group=PaginatorViewsTest.group,
            )

    def test_first_page_containse_ten_records(self):
        templates_names = {
            'index': {},
            'group_posts': {'slug': 'test-slug'}
        }
        for reverse_name, kwargs in templates_names.items():
            with self.subTest():
                response = PaginatorViewsTest.guest_client.get(
                    reverse(reverse_name, kwargs=kwargs)
                )
                self.assertEqual(
                    len(response.context.get('page').object_list), 10
                )

    def test_second_page_containse_three_records(self):
        templates_names = {
            'index': {},
            'group_posts': {'slug': 'test-slug'}
        }
        for reverse_name, kwargs in templates_names.items():
            with self.subTest():
                response = PaginatorViewsTest.guest_client.get(
                    reverse(reverse_name, kwargs=kwargs) + '?page=2'
                )
                self.assertEqual(
                    len(response.context.get('page').object_list), 3
                )
