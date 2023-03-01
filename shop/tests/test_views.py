from django.test import TestCase, Client
from shop.models import Item, Category, ItemImage, OrderItem, Order
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import faker


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.faker = faker.Faker()
        self.user = User.objects.create_user(username='testuser')
        self.user.set_password('12345')
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
        self.init_quantity = 5
        order_item = OrderItem.objects.create(
            item=self.item,
            user=self.user,
            ordered=False,
            quantity=self.init_quantity,
        )
        self.order = Order.objects.create(
            user=self.user, ordered_date=timezone.now())
        self.order.items.add(order_item)
        self.category.save()

    def test_item_detail_GET(self):
        response = self.client.get(reverse('item_detail', kwargs={'slug': self.item.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/item_detail.html')

    def test_category_items_GET(self):
        response = self.client.get(reverse('category_items', kwargs={'slug': self.category.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.context['response'].number, 1)
        self.assertTemplateUsed(response, 'shop/category_items.html')

    def test_category_items_GET_empty_page(self):
        response = self.client.get(
            reverse('category_items', kwargs={'slug': self.category.slug}),
            {"page": self.faker.random_int(min=500, max=1000)}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.context['response'].number, response.context['response'].paginator.num_pages)
        self.assertTemplateUsed(response, 'shop/category_items.html')
