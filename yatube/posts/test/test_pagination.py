from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group, User
from posts.views import POSTS_ON_PAGE


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='test group',
            slug='test_slug',
            description='test description',
        )
        cls.post_list = []
        cls.posts = []
        cls.amount_posts = 13
        for i in range(0, cls.amount_posts):
            cls.posts.append(
                Post(text=f'#{i} Текст тестового поста #{i}',
                     author=cls.user, group=cls.group,)
            )
        cls.post_list = Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):

        POSTS_ON_LAST_PAGE = self.amount_posts % POSTS_ON_PAGE
        first_page = {
            reverse('posts:index'): POSTS_ON_PAGE,
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}): POSTS_ON_PAGE,
            reverse('posts:profile', kwargs={'username': self.user}
                    ): POSTS_ON_PAGE,
            reverse('posts:index') + '?page=2': POSTS_ON_LAST_PAGE,
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}
                    ) + '?page=2': POSTS_ON_LAST_PAGE,
            reverse('posts:profile',
                    kwargs={'username': self.user}
                    ) + '?page=2': POSTS_ON_LAST_PAGE,
        }
        for value, expected in first_page.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertEqual(
                    len(response.context['page_obj']), expected)
