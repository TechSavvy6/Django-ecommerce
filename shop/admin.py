from django.contrib import admin
from .models import Item, ItemImage, Category, Order, OrderItem, Coupon
# Register your models here.


class ItemImageAdmin(admin.StackedInline):
    model = ItemImage


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    inlines = [ItemImageAdmin]
    list_display = ['name', 'price', 'category', 'quantity']
    search_fields = ['name']
    list_filter = ['category']


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = [
        'user__username',
        'ref_code'
    ]
    list_filter = ['ordered', 'being_delivered',
                   'received', 'ordered_date']

    list_display = ['user', 'ordered',
                    'being_delivered', 'received', 'get_total']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    search_fields = ['code']
    list_display = ['code', 'amount', 'is_expired']


admin.site.register(OrderItem)
