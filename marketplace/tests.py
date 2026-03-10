from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.urls import reverse

from .models import Listing


# Create your tests here.

class ListingOrderTest(TestCase):
    """Ensure that the admin listing list is sorted by `id` when no status
    filter is provided (i.e. the frontend "Tất cả" tab).
    """

    def setUp(self):
        # superuser required by IsAdminUser permission
        self.admin = User.objects.create_superuser('admin', 'admin@example.com', 'pass')
        # a seller for the listings
        self.seller = User.objects.create_user('seller', 'seller@example.com', 'pass')
        # create two listings; auto-increment ids ensure order
        Listing.objects.create(seller=self.seller, title='First', price=1)
        Listing.objects.create(seller=self.seller, title='Second', price=2)

        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_all_sorted_by_id(self):
        url = reverse('admin-listings-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        ids = [item['id'] for item in data]
        self.assertEqual(ids, sorted(ids))

    def test_filtered_sorted_by_id(self):
        # even when requesting a specific status, order should still be by id
        Listing.objects.all().update(status='PENDING')
        url = reverse('admin-listings-list') + '?status=PENDING'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        ids = [item['id'] for item in data]
        self.assertEqual(ids, sorted(ids))
