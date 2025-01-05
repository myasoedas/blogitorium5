from django.contrib.sitemaps import Sitemap
from taggit.models import Tag
from django.urls import reverse
from .models import Post


class PostSitemap(Sitemap):
    changefreg = 'weekly'
    priority = 0.9

    def items(self):
        return Post.published.all()

    def lastmod(self, obj):
        return obj.updated


class TagSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return Tag.objects.all()

    def location(self, obj):
        return reverse('blog:post_list_by_tag', args=[obj.slug])
