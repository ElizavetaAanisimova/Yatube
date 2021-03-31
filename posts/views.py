from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'index.html',
        {'page': page, 'is_short': True}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'group.html',
        {
            'group': group, 'page': page,
            'is_short': True
        })


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    user_posts = user.posts.all()
    post_count = user_posts.count()
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author__username=username).exists()
    else:
        following = False
    return render(
        request, 'profile.html', {
            'author': user, 'post_count': post_count,
            'page': page, 'following': following, 'is_short': True
        })


def post_view(request, username, post_id):
    user_post = get_object_or_404(Post, author__username=username, id=post_id)
    post_count = user_post.author.posts.count()
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post__id=post_id)
    return render(
        request, 'post.html',
        {
            'author': user_post.author,
            'post_count': post_count,
            'user_post': user_post,
            'form': form,
            'comments': comments,
        })


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if post.author != request.user:
        return redirect('post', username, post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)
    return render(
        request, 'new.html', {'form': form, 'post': post, 'is_edit': True}
    )


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('post', username, post_id)
    return render(
        request, 'includes/comments.html',
        {'form': form, 'user_post': post, 'author': post.author}
    )


@login_required
def follow_index(request):
    author_posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(author_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'follow.html', {'page': page, 'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    follow_user = get_object_or_404(User, username=username)
    if request.user != follow_user:
        Follow.objects.get_or_create(user=request.user, author=follow_user)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    unfollow_user = get_object_or_404(User, username=username)
    get_object_or_404(
        Follow,
        user=request.user,
        author=unfollow_user
    ).delete()
    return redirect('profile', username=username)
