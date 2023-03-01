from django.test import TestCase
from users.models import User, Address, UserProfile
from faker import Faker


class TestModels(TestCase):
    def setUp(self):
        self.faker = Faker(["nl_NL"])
        self.user = User.objects.create(
            username=self.faker.user_name(),
            email=self.faker.email(),
        )
        self.user.set_password(self.faker.text(max_nb_chars=10))
        self.user.save()
        self.profile = UserProfile.objects.create(
            phone_no="+923111234567",
            user=self.user
        )
        self.address = Address.objects.create(
            street_address=self.faker.street_address(),
            city=self.faker.city(),
            postal_code=self.faker.postcode(),
            user=self.user
        )
        super().setUp()

    def test_user_profile(self):
        self.assertEqual(str(self.profile), self.user.username)

    def test_address(self):
        self.assertEquals(str(self.address), self.user.username)
