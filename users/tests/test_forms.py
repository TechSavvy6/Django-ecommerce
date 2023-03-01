from django.test import TestCase
from users.forms import SignupForm
from django.urls import reverse
from django.contrib.auth import get_user_model
from faker import Faker


class TestForms(TestCase):
    def setUp(self):
        faker = Faker(["nl_NL"])
        self.signup_data = {
            'username': faker.user_name(),
            'email': faker.email(),
            'phone_no': "+923111234567",
            'password1': "lkjh@1234",
            'password2': "lkjh@1234"
        }
        super().setUp()

    def test_signup_is_valid(self):
        form = SignupForm(data=self.signup_data)
        self.assertTrue(form.is_valid())

    def test_signup_create_user(self):
        response = self.client.post(reverse('account_signup'), data=self.signup_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(get_user_model().objects.exists())
