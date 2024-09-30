from django.contrib.sitemaps import Sitemap
from .models import Story

class StorySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Story.objects.all()

    def lastmod(self, obj):
        return obj.updated_at
