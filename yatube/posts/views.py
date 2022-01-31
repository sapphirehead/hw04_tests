from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Group, User
from .forms import PostForm


LIMIT = 10


def index(request):
    """Сохраняем в posts объекты модели Post,
    отсортированные по полю pub_date по убыванию.
    """
    posts_list = Post.objects.all()
    # Показывать по 10 записей на странице.
    paginator = Paginator(posts_list, LIMIT)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """View-функция для страницы сообщества.
    Страница с информацией о постах отфильтрованных по группам.
    Принимает параметр slug из path()
    """
    groups_list = get_object_or_404(Group, slug=slug)
    posts_list = groups_list.posts.all()
    paginator = Paginator(posts_list, LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': groups_list,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """View-функция для отображения профиля пользователя.
    Принимает параметр username из path()
    """
    user = get_object_or_404(User, username=username)
    posts_list = Post.objects.select_related('author').filter(author=user)
    paginator = Paginator(posts_list, LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': user,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """View-функция для отображения отдельного поста пользователя.
    Принимает порядковый номер поста из path()
    """
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """View-функция для создания отдельного поста пользователя."""
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect("posts:profile", username=post.author)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """View-функция для редактирования отдельного поста пользователя.
    Принимает порядковый номер поста из path()
    """
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id=post_id)
    context = {
        'form': form,
        'post_id': post_id,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)
