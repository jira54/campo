from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Customer, LoyaltyReward


User = get_user_model()


class CustomerFlowTests(TestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(email='t@vendor.test', business_name='Test Biz', owner_name='Owner', phone_number='0700000000', password='testpass')
        self.client.force_login(self.vendor)

    def test_add_new_customer_creates_record(self):
        url = reverse('vendors:customers')
        resp = self.client.post(url, {'name': 'Test Customer', 'phone_number': '0712345678'})
        self.assertEqual(resp.status_code, 302)
        c = Customer.objects.filter(vendor=self.vendor, phone_number='0712345678').first()
        self.assertIsNotNone(c)
        self.assertEqual(c.visit_count, 1)

    def test_record_visit_increments(self):
        c = Customer.objects.create(vendor=self.vendor, name='Repeat', phone_number='0711111111', visit_count=1)
        url = reverse('vendors:customers')
        resp = self.client.post(url, {'name': 'Repeat', 'phone_number': '0711111111'})
        self.assertEqual(resp.status_code, 302)
        c.refresh_from_db()
        self.assertEqual(c.visit_count, 2)


class LoyaltyTests(TestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(email='l@vendor.test', business_name='Loyal', owner_name='Owner', phone_number='0700000001', password='testpass')
        self.client.force_login(self.vendor)

    def test_loyalty_eligibility(self):
        c = Customer.objects.create(vendor=self.vendor, name='Loyal Cust', phone_number='0722222222', visit_count=4)
        r = LoyaltyReward.objects.create(vendor=self.vendor, reward_name='Free Coffee', required_visits=5)
        url = reverse('vendors:loyalty')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # verify reward is shown in the template
        self.assertContains(resp, 'Free Coffee')
        self.assertContains(resp, '5')
