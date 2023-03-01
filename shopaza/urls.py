from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from shop.sitemaps import ItemSitemap, CategorySitemap
from django.conf.urls.i18n import i18n_patterns
from shop.views import stripe_webhook

sitemaps = {
    "items": ItemSitemap(),
    "categories": CategorySitemap(),
}


urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', include('robots.urls')),
    path('webhooks/stripe/', stripe_webhook, name="stripe_webhook"),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('users/', include('users.urls')),
    path('', include('core.urls')),
    path('shop/', include('shop.urls')),
)

if settings.DEBUG is not False:
    import debug_toolbar
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += path('__debug__/', include(debug_toolbar.urls)),
