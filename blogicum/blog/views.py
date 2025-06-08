from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import CommentForm, PostForm, UserEditForm
from .models import Category, Comment, Post


User = get_user_model()


SELECT_LIMIT = 10


def query_set(filter=None, annotate=None):
    query_set = Post.objects.select_related(
        'category',
        'location',
        'author'
    )
    if filter:
        query_set = query_set.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.now()
        )
    if annotate:
        query_set = query_set.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    return query_set


class DispatchMixin:
    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != self.request.user:
            return redirect('blog:post_id', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class ProfileGetSuccessUrlMixin:
    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostIdGetSuccessUrlMixin:
    def get_success_url(self):
        instance = self.get_object()
        return reverse('blog:post_id', kwargs={'post_id': instance.pk})


class IndexListView(ListView):
    """Отображаем на главной странице список объектов из базы данных"""

    template_name = 'blog/index.html'
    paginate_by = SELECT_LIMIT
    queryset = query_set(filter=True, annotate=True)


class PostDetailView(DetailView):
    """Отображаем отдельный пост"""

    queryset = query_set()
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        instance = super().get_object(queryset=queryset)
        if instance.author != self.request.user and (
            not instance.category.is_published
            or not instance.is_published
            or instance.pub_date > timezone.now()
        ):
            raise Http404('Post not found')
        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        form = CommentForm()
        comments = post.comments.select_related('author').order_by(
            'created_at'
        )
        context.update({'post': post, 'form': form, 'comments': comments})
        return context


class PostCreateView(
    LoginRequiredMixin,
    ProfileGetSuccessUrlMixin,
    CreateView
):
    """Создание поста одного из пользователей"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(
    LoginRequiredMixin,
    DispatchMixin,
    PostIdGetSuccessUrlMixin,
    UpdateView
):
    """Редактирование поста"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class PostDeleteView(LoginRequiredMixin, DispatchMixin, DeleteView):
    """Удаление поста"""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')


class CategoryPostsListView(ListView):
    """Отображение категорий, которые связаны с разными постами"""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = SELECT_LIMIT

    def get_queryset(self):
        category = get_object_or_404(
            Category.objects.filter(
                slug=self.kwargs['category_slug'],
                is_published=True
            )
        )
        post_list = query_set(
            filter=True, annotate=True
        ).filter(category=category)
        return post_list

    def get_object(self, queryset=None):
        return get_object_or_404(
            Category.objects.values(
                'title',
                'description'
            ).filter(
                slug=self.kwargs['category_slug'],
                is_published=True,
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        context['category'] = category
        return context


class CommentCreateView(
    LoginRequiredMixin,
    PostIdGetSuccessUrlMixin,
    CreateView
):
    """Можно создать комментарий к посту"""

    model = Post
    form_class = CommentForm
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.get_object()
        return super().form_valid(form)


class CommentUpdateView(
    LoginRequiredMixin,
    DispatchMixin,
    PostIdGetSuccessUrlMixin,
    UpdateView
):
    """Возможность редактирования комментария"""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        context.update({'comment': comment})
        return context


class CommentDeleteView(
    LoginRequiredMixin,
    DispatchMixin,
    PostIdGetSuccessUrlMixin,
    DeleteView
):
    """Возможность удалить комментарий"""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class ProfileListView(ListView):
    """Отображение профиля зарегистрированного пользователя"""

    template_name = 'blog/profile.html'
    paginate_by = SELECT_LIMIT

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        profile = self.get_object()
        return query_set(
            filter=self.request.user != profile,
            annotate=True
        ).filter(author=profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        context['profile'] = profile
        return context


class ProfileUpdateView(
    LoginRequiredMixin,
    ProfileGetSuccessUrlMixin,
    UpdateView
):
    """Редактирование профиля"""

    form_class = UserEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user
