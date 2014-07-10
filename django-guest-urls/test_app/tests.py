# -*- coding: utf-8 -*-
"""Test the guest-urls models."""
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory


from guest_urls.models import GuestUrl


class GuestUrlModelTests(TestCase):
    """Basic model property and method tests."""

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='bob', email='bob@example.com')

    def _assert_link_works(self, url):
        """Common guest url assertions."""
        guest_url = GuestUrl(source_url=url)
        guest_url.save()
        self.assertEqual(guest_url.used_to_date, 0)
        request = self.factory.get(url)
        request.user = self.user
        response = guest_url.process_request(request)
        self.assertContains(response, "OK", status_code=200)
        # refresh the instance to pick up the new properties
        guest_url = GuestUrl.objects.get(id=guest_url.id)
        self.assertEqual(guest_url.used_to_date, 1)

    def test_link_args_0(self):
        self._assert_link_works(reverse('test_link_args_0'))

    def test_link_args_1(self):
        self._assert_link_works(reverse('test_link_args_1', args=['2014']))

    def test_link_args_2(self):
        self._assert_link_works(
            reverse('test_link_args_2', args=['2014', '07'])
        )

    def test_link_kwargs_1(self):
        self._assert_link_works(
            reverse('test_link_kwargs_1', kwargs={'year': '2014'})
        )

    def test_link_kwargs_2(self):
        self._assert_link_works(
            reverse('test_link_kwargs_2', kwargs={'year': '2014', 'month': '07'})
        )
