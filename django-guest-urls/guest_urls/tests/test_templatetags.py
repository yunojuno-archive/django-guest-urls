# -*- coding: utf-8 -*-
"""Test the guest-urls models."""
from django.test import TestCase

from guest_urls.models import GuestUrl
from guest_urls.templatetags import guest_url_tags
from guest_urls.templatetags.guest_url_tags import try_parse_date


class GuestUrlTemplateFilterTests(TestCase):

    def _assert_usage(self, usage, max_uses, expires_at):
        """Run assertions for a usage string."""
        url = "/a/b/c"
        new_url = guest_url_tags.guest_url(url, usage)
        # de facto assertion that there is only one instance
        guest_url = GuestUrl.objects.get()
        self.assertEqual(new_url, guest_url.get_absolute_url())
        self.assertEqual(guest_url.max_uses, max_uses)
        self.assertEqual(guest_url.expires_at, expires_at)
        guest_url.delete()

    def test_simple_url(self):
        "Test a simple URL with no arguments"
        self._assert_usage(None, -1, None)

    def test_simple_url_1(self):
        "Test a simple URL with an empty string argument"
        self._assert_usage("", -1, None)

    def test_max_uses(self):
        "Confirm that we can pass in max_uses as an integer"
        self._assert_usage("1", 1, None)

    def test_max_uses_100(self):
        "Confirm that we can pass in max_uses as an integer"
        self._assert_usage("100", 100, None)

    def test_expiry_date(self):
        "Confirm that we can pass in expires_at as an iso-date."
        self._assert_usage("2014-07-12", -1, try_parse_date("2014-07-12"))
        self._assert_usage("2014-07-12 09:00", -1, try_parse_date("2014-07-12 09:00"))

    def test_expiry_date_and_expires(self):
        "Confirm that we can pass in expires_at and uses, in any order."
        self._assert_usage("1, 2014-07-12", 1, try_parse_date("2014-07-12"))
        self._assert_usage("2014-07-12, 1", 1, try_parse_date("2014-07-12"))

    def test_too_many_args_error(self):
        "Confirm AssertionError if too many args supplied."
        self.assertRaises(AssertionError, guest_url_tags.guest_url, '/', '1,2,3')

    def test_unparseable_args_error(self):
        "Confirm ValueError if unparseable args supplied."
        self.assertRaises(ValueError, guest_url_tags.guest_url, '/', 'foobar')
