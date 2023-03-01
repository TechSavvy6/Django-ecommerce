# import random
import faker.providers
from django.core.management.base import BaseCommand
from faker import Faker
# from shop.models import Category, Item, ItemImage
# from users.models import Address
# import urllib.request
# from PIL import Image
# import os
# from django.core.files import File
# from django.contrib.auth.models import User

CATEGORIES = [
    ["Shoes", "أحذية"],
    ["Books", "كتب"],
    ["Trainers", "المدربون"],
    ["Clothes", "ملابس"],
    ["Dress", "فستان"],
    ["T-shirt", "تي شيرت"],
    ["Jeans", "جينز"],
    ["Shirts", "قمصان"],
    ["Garden Outdoors", "حديقة في الهواء الطلق"],
    ["Health Personal Care", "العناية الشخصية الصحية"],
    ["Grocery", "خضروات"],
]


class Provider(faker.providers.BaseProvider):
    def ecommerce_category(self):
        return self.random_element(CATEGORIES)


class Command(BaseCommand):
    help = "Command information"

    def handle(self, *args, **kwargs):
        fake = Faker(["nl_NL"])
        fake.add_provider(Provider)

        # ? Categories
        # for i in range(len(CATEGORIES)):
        #     Category.objects.create(name_en=CATEGORIES[i][0], name_ar=CATEGORIES[i][1])
        # ? Items
        # for _ in range(16):
        #     pt = fake.text(max_nb_chars=25)
        #     c = random.choice(list(Category.objects.all()))
        #     price = round(random.uniform(20, 1000), 2)
        #     discount_price = round(random.uniform(10, price), 2)
        #     print(Item.objects.create(
        #         category_id=c.id,
        #         name=pt,
        #         description=fake.text(max_nb_chars=100),
        #         price=price,
        #         discount_price=discount_price,
        #         quantity=round(random.uniform(10, 100))
        #     ))
        # # ? Item Images
        # for i in list(Item.objects.filter(name="Cupiditate modi maiores.")):
        #     for _ in range(3):
        #         file_name = fake.file_name(extension='png', category="image")
        #         res = urllib.request.urlretrieve(
        #             f'https://source.unsplash.com/1920x1080/?Shirts', file_name)
        #         ItemImage.objects.create(image=File(open(file_name, 'rb')), item=i)
        # user = User.objects.first()
        # for _ in range(5):
        #     Address.objects.create(name=fake.text(
        #         max_nb_chars=15), address=fake.address(), user=user)

        self.stdout.write(self.style.SUCCESS("Done"))
