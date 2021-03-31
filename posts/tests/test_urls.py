from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(
            username='TestName',
            email='Test@yandex.ru',
            password='test01'
        )

        cls.user1 = User.objects.create(
            username='TestName1',
            email='Test1@yandex.ru',
            password='test00'
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

    def setUp(self):
        self.guest_client = Client()
        self.user = PostURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)

    def test_homepage(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group(self):
        """Страница /group/<slug:slug>/ доступна любому пользователю."""
        response = self.guest_client.get(reverse(
            'group_posts',
            kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.status_code, 200)

    def test_username(self):
        """Страница /<username>/ доступна любому пользователю."""
        response = self.guest_client.get(reverse(
            'profile',
            kwargs={'username': self.user.username})
        )
        self.assertEqual(response.status_code, 200)

    def test_username_post_id(self):
        """Страница /<username>/<post_id>/ доступна любому пользователю."""
        response = self.guest_client.get(reverse(
            'post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            })
        )
        self.assertEqual(response.status_code, 200)

    def test_new(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_new_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /new/ перенаправит
        анонимного пользователя на страницу логина."""
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_edit(self):
        """Страница /edit/ доступна автору."""
        response = self.authorized_client.get(reverse(
            'post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            })
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_redirect_non_author(self):
        """Страница по /new/ при редактировании перенаправит не автора."""
        response = self.authorized_client1.get(reverse(
            'post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            })
        )
        self.assertEqual(response.status_code, 302)

    def test_edit_redirect_non_author_on_post(self):
        """Страница /new/ при редактировании перенаправляет
        не автора на страницу поста."""
        response = self.authorized_client1.get(reverse(
            'post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }),
            follow=True
        )
        self.assertRedirects(
            response, reverse('post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            })
        )

    def test_edit_redirect_anonymous(self):
        """Страница по /new/ при редактировании перенаправит
        анонимного пользователя."""
        response = self.guest_client.get(reverse(
            'post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            })
        )
        self.assertEqual(response.status_code, 302)

    def test_edit_redirect_anonymous_on_login(self):
        """Страница /new/ при редактировании перенаправляет
        анонимного пользователя на страницу логина."""
        response = self.guest_client.get(reverse(
            'post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }),
            follow=True
        )
        kwargs = {'username': self.user.username, 'post_id': self.post.id}
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('post_edit', kwargs=kwargs)}"
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            reverse(
                'group_posts',
                kwargs={'slug': self.group.slug}
            ): 'group.html',
            '/new/': 'new.html',
            reverse(
                'post_edit', kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }): 'new.html'
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_404(self):
        """Cервер возвращает код 404, если страница не найдена."""
        response = self.guest_client.get('/notfound/')
        self.assertEqual(response.status_code, 404)

    def test_comment_redirect_redirect_anonymous(self):
        """Страница /add_comment/ при комментировании перенаправляет
        анонимного пользователя"""
        response = self.guest_client.get(reverse(
            'add_comment', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            })
        )
        self.assertEqual(response.status_code, 302)

    def test_add_comment_anonymous_on_login(self):
        """Страница /add_comment/ при комментировании перенаправляет
        анонимного пользователя на страницу логина."""
        response = self.guest_client.get(reverse(
            'add_comment', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }),
            follow=True
        )
        kwargs = {'username': self.user.username, 'post_id': self.post.id}
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('add_comment', kwargs=kwargs)}"
        )
