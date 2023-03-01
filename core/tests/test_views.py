from django.test import TestCase, Client
from django.urls import reverse
from core.templatetags import my_tags
from faker import Faker


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.faker = Faker(["nl_NL"])

    def test_index_GET(self):
        # ! Test View Without Page Parameter
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.context['response'].number, 1)
        self.assertTemplateUsed(response, 'core/index.html')

    def test_index_GET_empty_page(self):
        # ! Test View with Out of range Page Parameter
        response = self.client.get(reverse('index'), {"page": self.faker.random_int(min=500, max=1000)})
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.context['response'].number, response.context['response'].paginator.num_pages)
        self.assertTemplateUsed(response, 'core/index.html')

    def test_contact_GET(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/contact.html')

    def test_template_tag(self):
        response = self.client.get(reverse('index'), {"page": 1, "price__gt": ""})
        self.assertNotEquals(
            response.context['response'].number, my_tags.url_replace(response.context, page=2).split('=')[1]
        )
