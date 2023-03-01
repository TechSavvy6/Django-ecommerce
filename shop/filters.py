import django_filters
from .models import Item


class ItemFIlters(django_filters.FilterSet):
    class Meta:
        model = Item
        fields = {
            'price': ['gt', 'lt']
        }
