from django.shortcuts import render
from meta.views import Meta
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from shop.models import Item, Category
from shop.filters import ItemFIlters
from django.conf import settings
# Create your views here.


def index(request):
    queryset = Item.objects.all().select_related('category')
    meta = Meta(
        title=_("Shopaza"),
        description=settings.CONFIG.get('description'))

    categories = Category.objects.all()

    filtered_items = ItemFIlters(request.GET, queryset)
    filtered_items_form = filtered_items.form

    filtered_items_qs = filtered_items.qs
    paginator = Paginator(filtered_items_qs, 9)

    page = request.GET.get('page')
    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)

    return render(request, 'core/index.html', {
        'response': response,
        'filtered_qs_form': filtered_items_form,
        'categories': categories,
        "meta": meta
    })


def contact(request):
    meta = Meta(
        title=_("Contact Us"),
        description=_(
            '''Give us a call or drop by anytime, we endeavour to answer all enquiries within 24 hours on business
            days. We will be happy to answer your questions.'''),
    )
    return render(request, 'core/contact.html', {"meta": meta})
