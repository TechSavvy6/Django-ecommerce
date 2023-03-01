from django.db import models
from django.utils.translation import get_language, gettext_lazy as _
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from .utils import unique_slug_generator, unique_slug_generator_for_category
from django.db.models.signals import post_save

from datetime import date
from meta.models import ModelMeta
from django.urls import reverse
from users.models import Address
from django.conf import settings
# Create your models here.
User = get_user_model()


class Category(ModelMeta, models.Model):
    name_en = models.CharField(max_length=50)
    name_ar = models.CharField(max_length=50)
    slug = models.SlugField(max_length=500, blank=True, null=True)

    _metadata = {
        'title': 'name_ar' if (get_language() == "ar") else 'name_en',
        'description': settings.CONFIG.get('description')
    }

    class Meta:
        ordering = ("name_en",)
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name_en

    def get_absolute_url(self):
        return reverse("category_items", kwargs={"slug": self.slug})


class Item(ModelMeta, models.Model):
    name = models.CharField(max_length=450)
    price = models.IntegerField()
    discount_price = models.IntegerField(blank=True, null=True)
    category = models.ForeignKey(
        Category, related_name="items", on_delete=models.CASCADE)
    slug = models.SlugField(max_length=500, blank=True, null=True)
    description = models.TextField()
    quantity = models.IntegerField(default=1)
    date_time = models.DateTimeField(auto_now_add=True)

    _metadata = {
        'title': 'name',
        'description': 'description',
        'image': 'get_meta_image'
    }

    class Meta:
        ordering = ("-date_time",)
        verbose_name = _("Item")
        verbose_name_plural = _("Items")

    def __str__(self):
        return self.name

    def get_meta_image(self):  # pragma: no cover
        return self.images.first().image.url

    @property
    def is_available(self):
        if self.quantity > 0:
            return True
        else:
            return False

    def get_absolute_url(self):
        return reverse("item_detail", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("add_to_cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("remove_from_cart", kwargs={
            'slug': self.slug
        })

    def get_remove_single_item_from_cart_url(self):
        return reverse("remove_single_item_from_cart", kwargs={
            'slug': self.slug
        })


class ItemImage(models.Model):
    image = models.ImageField(upload_to="shopaza/item_images")
    item = models.ForeignKey(
        Item, related_name="images", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("ItemImage")
        verbose_name_plural = _("ItemImages")

    def __str__(self):
        return self.item.name


class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        verbose_name = _("OrderItem")
        verbose_name_plural = _("OrderItems")

    def __str__(self):
        return f"{self.quantity} of {self.item} - {self.user}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    # ? Set This on Checkout
    delivery_address = models.ForeignKey(
        Address, related_name='delivery_address', on_delete=models.SET_NULL, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    coupon = models.OneToOneField(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)

    class Meta:
        ordering = ("ordered_date",)
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"{self.user}"

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon and not self.coupon.is_expired:
            total -= self.coupon.amount
        return total


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.IntegerField()
    expiry = models.DateField()

    def __str__(self):
        return self.code

    @property
    def is_expired(self):
        if (self.expiry - date.today()).days > 0:
            return False
        else:
            return True


@receiver(post_save, sender=Category)
def category_slug_generator(sender, instance, created, **kwargs):
    if created:
        instance.slug = unique_slug_generator_for_category(instance)
        instance.save()


@receiver(post_save, sender=Item)
def item_slug_generator(sender, instance, created, **kwargs):
    if created:
        instance.slug = unique_slug_generator(instance)
        instance.save()
