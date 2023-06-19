from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group, User
from django.core.cache import cache


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        # Неавторизованный пользователь
        self.guest_client = Client()
        # Авторизованный
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "reverse(name): имя_html_шаблона:"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse('posts:group_posts', kwargs={'slug': self.group.slug})
             ): 'posts/group_list.html',
            (reverse('posts:profile', kwargs={'username': self.user})
             ): 'posts/profile.html',
            (reverse('posts:post_edit', kwargs={'post_id': self.post.id})
             ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            (reverse('posts:post_detail', kwargs={'post_id': self.post.id})
             ): 'posts/post_detail.html',
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        First_object = response.context['post']
        post_author_0 = First_object.author.username
        post_text_0 = First_object.text
        post_group_0 = First_object.group.title
        self.assertEqual(post_author_0, 'test_user')
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_group_0, 'Тестовая группа')

    def test_cash(self):
        response1 = self.guest_client.get(reverse('posts:index'))
        first_check = response1.content
        Post.objects.get(id=1).delete()
        response2 = self.guest_client.get(reverse('posts:index'))
        seconf_check = response2.content
        self.assertEqual(first_check, seconf_check)
