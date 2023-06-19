from django.test import TestCase, Client
from posts.models import Post, Group, User
from django.core.cache import cache


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Anb')
        cls.group = Group.objects.create(
            title='test group',
            slug='dd',
            description='test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/dd/',
            'posts/profile.html': '/profile/Anb/',
            'posts/post_detail.html': '/posts/1/',
            'posts/create_post.html': '/create/',
        }

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        for template, address in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        normal = 200
        redirect = 302
        not_found = 404
        response = self.guest_client.get(self.templates_url_names[
            'posts/index.html'])
        self.assertEqual(response.status_code, normal)

        response = self.guest_client.get(self.templates_url_names[
            'posts/group_list.html'])
        self.assertEqual(response.status_code, normal)

        response = self.guest_client.get(self.templates_url_names[
            'posts/profile.html'])
        self.assertEqual(response.status_code, normal)

        response = self.guest_client.get(self.templates_url_names[
            'posts/post_detail.html'])
        self.assertEqual(response.status_code, normal)

        response = self.guest_client.get('122')
        self.assertEqual(response.status_code, not_found)

        response = self.authorized_client.get(self.templates_url_names[
            'posts/create_post.html'])
        self.assertEqual(response.status_code, normal)

        response = self.guest_client.get(self.templates_url_names[
            'posts/create_post.html'])
        self.assertEqual(response.status_code, redirect)
