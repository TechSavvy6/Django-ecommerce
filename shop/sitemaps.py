from django.contrib.sitemaps import Sitemap
from .models import Item, Category


class ItemSitemap(Sitemap):  # pragma: no cover
    changeFreq = "weekly"
    priority = 0.5

    def items(self):
        return Item.objects.all()


class CategorySitemap(Sitemap):  # pragma: no cover
    changeFreq = "weekly"
    priority = 0.5

    def items(self):
        return Category.objects.all()
