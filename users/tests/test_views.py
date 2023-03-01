from django.test import TestCase, Client
from django.urls import reverse
from users.models import UserProfile, Address
from django.contrib.auth.models import User
from faker import Faker


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.faker = Faker(["nl_NL"])
        self.user = User.objects.create(
            username=self.faker.user_name(),
            email=self.faker.email(),
        )
        self.user.set_password("lkjh@1234")
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

    def test_settings_GET(self):
        assert self.client.login(username=self.user.username, password="lkjh@1234")
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/settings.html')

    def test_edit_phone_no_GET(self):
        assert self.client.login(username=self.user.username, password="lkjh@1234")
        response = self.client.get(reverse('edit_phone_no'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/edit_phone_no.html')

    def test_edit_phone_no_POST(self):
        assert self.client.login(username=self.user.username, password="lkjh@1234")
        new_phone_no = "+923117654321"
        response = self.client.post(reverse('edit_phone_no'), data={
            'phone_no': new_phone_no
        })
        self.assertEqual(response.status_code, 302)

    def test_update_profile_picture_GET(self):
        assert self.client.login(username=self.user.username, password="lkjh@1234")
        response = self.client.get(reverse('update_profile_picture'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/update_profile_picture.html')

    def test_delete_account_GET(self):
        assert self.client.login(username=self.user.username, password="lkjh@1234")
        response = self.client.get(reverse('delete_account'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/delete_account.html')

    def test_delete_account_POST_valid(self):
        assert self.client.login(username=self.user.username, password="lkjh@1234")
        response = self.client.post(reverse('delete_account'), {
            "delete_checkbox": True
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.exists())

    def test_delete_account_POST_invalid(self):
        assert self.client.login(username=self.user.username, password="lkjh@1234")
        response = self.client.post(reverse('delete_account'), {
            "delete_checkbox": False
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.exists())
