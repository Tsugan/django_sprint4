from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.db.models import Count, Prefetch
from django.core.paginator import Paginator

from .models import Category, Post, Comment, User
from .forms import PostForm, CommentForm, UserProfileForm
from .mixins import PostChangeMixin, CommentMixin

POST_COUNT = 10
PAGE_QUERY_PARAM = 'page'


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POST_COUNT

    def get_queryset(self):
        return Post.published.select_related(
            'category', 'location', 'author'
        ).annotate(comment_count=Count('comments'))


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.object
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('post')
        return context


class PostUpdateView(PostChangeMixin, UpdateView):
    pass


class PostDeleteView(PostChangeMixin, DeleteView):
    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(
            is_published=True, slug=category_slug
        ).prefetch_related(
            Prefetch(
                'post_set',
                Post.published.select_related(
                    'category', 'location', 'author'
                ).annotate(comment_count=Count('comments')),
                'filtered_posts',
            )
        )
    )
    paginator = Paginator(category.filtered_posts, POST_COUNT)
    page_number = request.GET.get(PAGE_QUERY_PARAM)
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'category': category}
    return render(request, template, context)


def profile(request, username):
    posts = (
        Post.published if request.user.username != username else Post.objects
    )
    profile = get_object_or_404(
        User.objects.filter(username=username).prefetch_related(
            Prefetch(
                'post_set',
                posts.select_related('category', 'location', 'author')
                .order_by('-pub_date')
                .annotate(comment_count=Count('comments')),
                'all_posts',
            )
        )
    )
    paginator = Paginator(profile.all_posts, POST_COUNT)
    page_number = request.GET.get(PAGE_QUERY_PARAM)
    page_obj = paginator.get_page(page_number)
    context = {'profile': profile, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST' and request.user.is_authenticated:
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            return redirect('blog:profile', username=username)
    else:
        form = UserProfileForm(instance=request.user)
    context = {'form': form}
    return render(request, 'blog/user.html', context)


class CommentCreateView(LoginRequiredMixin, CreateView):
    post_object = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class CommentUpdateView(CommentMixin, UpdateView):
    pass


class CommentDeleteView(CommentMixin, DeleteView):
    pass
