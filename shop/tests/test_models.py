from django.test import TestCase, Client
from shop.models import Item, Category, ItemImage, OrderItem, Order, Coupon
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
import faker


class TestModels(TestCase):
    def setUp(self):
        self.faker = faker.Faker()
        self.user = User.objects.create(
            username=self.faker.user_name(),
            email=self.faker.email(),
        )
        self.user.set_password(self.faker.text(max_nb_chars=10))
        self.user.save()
        self.category = Category.objects.create(name_en=self.faker.word(), name_ar=self.faker.word())
        self.item = Item.objects.create(
            name=self.faker.word(),
            price=self.faker.random_number(digits=4),
            discount_price=self.faker.random_number(digits=2),
            category=self.category,
            description=self.faker.text(),
            quantity=self.faker.random_number(digits=2),
        )
        self.item_image = ItemImage.objects.create(
            item=self.item,
            image=self.faker.image_url(),
        )
        self.order_item = OrderItem.objects.create(
            item=self.item,
            quantity=self.faker.random_number(digits=1),
            user=self.user,
        )
        self.order = Order.objects.create(
            user=self.user,
            ordered_date=timezone.now(),
        )
        self.coupon = Coupon.objects.create(
            code=self.faker.word(),
            amount=10,
            expiry=date.today() + timedelta(days=1),
        )
        self.order.items.add(self.order_item)
        self.order.coupon = self.coupon
        self.order.save()
        self.client = Client()
        super().setUp()

    def test_category_model(self):
        self.assertEquals(str(self.category), self.category.name_en)
        response = self.client.get(self.category.get_absolute_url())
        self.assertEquals(response.status_code, 200)

    def test_item_model(self):
        self.assertEquals(str(self.item), self.item.name)
        response = self.client.get(self.item.get_absolute_url())
        self.assertEquals(response.status_code, 200)
        self.item.quantity = 0
        self.item.save()
        self.assertFalse(self.item.is_available)

    def test_item_model_add_to_cart_url(self):
        response = self.client.get(self.item.get_add_to_cart_url())
        self.assertEquals(response.status_code, 302)

    def test_item_model_remove_from_cart_url(self):
        response = self.client.get(self.item.get_remove_from_cart_url())
        self.assertEquals(response.status_code, 302)

    def test_item_model_remove_single_item_from_cart_url(self):
        response = self.client.get(self.item.get_remove_single_item_from_cart_url())
        self.assertEquals(response.status_code, 302)

    def test_item_image_model(self):
        self.assertEquals(str(self.item_image), self.item_image.item.name)

    def test_order_item_model(self):
        self.assertEquals(str(self.order_item), f"{self.order_item.quantity} of {self.item} - {self.user}")
        self.assertIsNotNone(self.order_item.get_total_item_price())
        self.assertIsNotNone(self.order_item.get_total_discount_item_price())
        self.assertIsNotNone(self.order_item.get_amount_saved())
        # ! With Discount Price
        self.assertIsNotNone(self.order_item.get_final_price())
        # ! Without Discount Price
        self.item.discount_price = None
        self.assertIsNotNone(self.order_item.get_final_price())

    def test_order_model(self):
        self.assertEquals(str(self.order), self.user.username)
        # ! With Valid Coupon
        self.assertIsNotNone(self.order.get_total())
        # ! With Invalid Coupon
        self.coupon.expiry = date.today() - timedelta(days=1)
        self.coupon.save()
        self.assertIsNotNone(self.order.get_total())
        # ! Without Coupon
        self.order.coupon = None
        self.assertIsNotNone(self.order.get_total())

    def test_coupon_model(self):
        self.assertEquals(str(self.coupon), self.coupon.code)
