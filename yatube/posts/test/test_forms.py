from posts.forms import PostForm
from posts.models import Post, Group, User, Comment, Follow
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache
import shutil
import tempfile

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user2 = User.objects.create_user(username='user_test_2')
        cls.group = Group.objects.create(
            title='Первая тестовая группа',
            slug='test_slug',
            description='Тестовое описание для первой тестовой группы',
        )
        cls.group2 = Group.objects.create(
            title='Вторая тестовая группа',
            slug='test_slug_2',
            description='Тестовое описание для второй тестовой группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.form = PostForm()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Неавторизованный пользователь
        self.guest_client = Client()
        # Авторизованный
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2.force_login(self.user2)
        cache.clear()

    def test_create_auth_post(self):
        posts_count = Post.objects.count()
        """Валидная форма создает запись в Post."""
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст авторизированного пользователя',
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.user}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст авторизированного пользователя',
            ).exists()
        )

    def test_create_guest_post(self):
        posts_count = Post.objects.count()
        """Валидная форма создает запись в Post."""
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст анонимного пользователя',
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, '/auth/login/?next=/create/')
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что создалась запись с заданным слагом
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый текст анонимного пользователя',
            ).exists()
        )

    def test_edit_auth_post(self):
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст измененый в перый раз',
            'group': self.group2.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(
            Post.objects.get(
                id=self.post.id
            ).text,
            'Тестовый текст измененый в перый раз'
        )

    def test_edit_guest_post(self):
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст измененый дважды',
            'group': self.group2.id,
            'image': uploaded,
        }
        self.assertEqual(
            Post.objects.get(
                id=self.post.id
            ).text,
            'Тестовый пост'
        )
        self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(
            Post.objects.get(
                id=self.post.id
            ).text,
            'Тестовый пост'
        )

    def test_edit_not_author_post(self):
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст измененый для не автора',
            'group': self.group2.id,
            'image': uploaded,
        }
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост'
            ).exists()
        )
        self.authorized_client2.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(
            Post.objects.get(
                id=self.post.id
            ).text,
            'Тестовый пост'
        )

    def test_auth_comment(self):
        comment_count = Comment.objects.filter(post=self.post).count()
        form_data = {
            'text': 'Тестовый комментарий авторизированного пользоватя',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.filter(post=self.post).count(),
                         comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый комментарий авторизированного пользоватя',
            ).exists()
        )

    def test_guest_comment(self):
        comment_count = Comment.objects.filter(post=self.post).count()
        form_data = {
            'text': 'Тестовый комментарий не авторизированного пользоватя',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.filter(post=self.post).count(),
                         comment_count)
        self.assertFalse(
            Comment.objects.filter(
                text='Тестовый комментарий не авторизированного пользоватя',
            ).exists()
        )

    def test_follow_unfollow_auth(self):
        follows_count = Follow.objects.filter(user=self.user2).count()
        self.authorized_client2.post(reverse('posts:profile_follow',
                                     kwargs={'username': self.user}))
        self.assertEqual(Follow.objects.filter(user=self.user2).count(),
                         follows_count + 1)
        self.authorized_client2.post(reverse('posts:profile_unfollow',
                                     kwargs={'username': self.user}))
        self.assertEqual(Follow.objects.filter(user=self.user2).count(),
                         follows_count)

    def test_double_follow_auth(self):
        first_follows_count = Follow.objects.filter(user=self.user2).count()
        self.authorized_client2.post(reverse('posts:profile_follow',
                                     kwargs={'username': self.user}))
        self.assertEqual(Follow.objects.filter(user=self.user2).count(),
                         first_follows_count + 1)
        second_follows_count = Follow.objects.filter(user=self.user2).count()
        self.authorized_client2.post(reverse('posts:profile_follow',
                                     kwargs={'username': self.user}))
        self.assertEqual(Follow.objects.filter(user=self.user2).count(),
                         second_follows_count)

    def test_self_follow(self):
        follows_count = Follow.objects.filter(user=self.user).count()
        self.authorized_client.post(reverse('posts:profile_follow',
                                    kwargs={'username': self.user}))
        self.assertEqual(Follow.objects.filter(user=self.user2).count(),
                         follows_count)

    def test_guest_follow(self):
        follows_count = Follow.objects.filter(user=self.user).count()
        self.guest_client.post(reverse('posts:profile_follow',
                               kwargs={'username': self.user}))
        self.assertEqual(Follow.objects.filter(user=self.user2).count(),
                         follows_count)

    def test_follow_post_appears(self):
        follows_count = Follow.objects.filter(user=self.user2).count()
        form_data = {
            'text': 'Тестовый текст авторизированного пользователя',
        }
        self.authorized_client2.post(reverse('posts:profile_follow',
                                     kwargs={'username': self.user}))
        self.assertEqual(Follow.objects.filter(user=self.user2).count(),
                         follows_count + 1)
        follow_posts_count = Post.objects.filter(
            author__following__user=self.user2).count()
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст авторизированного пользователя',
            ).exists()
        )
        self.assertEqual(Post.objects.filter(
            author__following__user=self.user2).count(),
            follow_posts_count + 1)

    def test_dont_follow_post_dont_appears(self):
        form_data = {
            'text': 'Тестовый текст авторизированного пользователя',
        }
        follow_posts_count = Post.objects.filter(
            author__following__user=self.user2).count()
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст авторизированного пользователя',
            ).exists()
        )
        self.assertEqual(Post.objects.filter(
            author__following__user=self.user2).count(),
            follow_posts_count)
