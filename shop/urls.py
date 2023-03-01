from django.urls import path
from .views import (
    ItemDetailView, category_items, add_to_cart, remove_from_cart,
    remove_single_item_from_cart, cart, checkout, add_coupon, remove_coupon, payment_successful, user_orders
)

urlpatterns = [
    path('items/<str:slug>/', ItemDetailView.as_view(), name="item_detail"),
    path('category/<str:slug>/', category_items, name="category_items"),
    path('add-to-cart/<slug>/', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove_from_cart'),
    path('remove-single-item-from-cart/<slug>/',
         remove_single_item_from_cart, name='remove_single_item_from_cart'),
    path('cart/', cart, name="cart"),
    path('checkout/', checkout, name="checkout"),
    path('add-coupon/', add_coupon, name="add_coupon"),
    path('remove-coupon/', remove_coupon, name="remove_coupon"),
    path('payment-successful/', payment_successful, name="payment_successful"),
    path('my-orders/', user_orders, name="user_orders"),
]
