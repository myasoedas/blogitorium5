from django.contrib.postgres.search import (
    SearchVector, SearchQuery, SearchRank, TrigramSimilarity
)
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from urllib.parse import urlencode

from taggit.models import Tag
from .forms import CommentForm, EmailPostForm, SearchForm
from .models import Post

POST_LIST_NUMBER = 10
SIMILAR_POSTS = 4


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, POST_LIST_NUMBER)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED, slug=post,
                             publish__year=year, publish__month=month, publish__day=day)
    comments_list = post.comments.filter(active=True)
    paginator = Paginator(comments_list, POST_LIST_NUMBER)
    page_number = request.GET.get('page', 1)
    try:
        comments = paginator.page(page_number)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)
    form = CommentForm()
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id).distinct()
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:SIMILAR_POSTS]
    return render(request, 'blog/post/detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'similar_posts': similar_posts
    })


def post_share(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} ({cd['email']}) recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, None, [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent
        }
    )


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        page_number = request.GET.get('page', 1)
        query_string = urlencode({'page': page_number})
        return redirect(f'{post.get_absolute_url()}?{query_string}')
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = POST_LIST_NUMBER
    template_name = 'blog/post/list.html'


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            if len(query) < 3:
                return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results, 'error': 'Search term must be at least 3 characters long.'})
            search_vector = SearchVector('title', weight='A', config='russian') + SearchVector('body', weight='B', config='russian')
            search_query = SearchQuery(query, config='russian', search_type='websearch')
            trigram_similarity = TrigramSimilarity('title', query)
            combined_results = Post.published.annotate(rank=SearchRank(search_vector, search_query), similarity=trigram_similarity).filter(rank__gte=0.3, similarity__gt=0.1).order_by('-rank', '-similarity')
            paginator = Paginator(combined_results, POST_LIST_NUMBER)
            page_number = request.GET.get('page', 1)
            try:
                results = paginator.page(page_number)
            except PageNotAnInteger:
                results = paginator.page(1)
            except EmptyPage:
                results = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results})
