from django.test import TestCase
from django.urls import reverse


class RecommendationsViewTests(TestCase):
    def test_page_loads(self):
        response = self.client.get(reverse('recommendations'))
        self.assertEqual(response.status_code, 200)
