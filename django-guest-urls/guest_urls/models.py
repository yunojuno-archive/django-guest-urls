# -*- coding: utf-8 -*-
"""guest_url models.

* GuestUrl
* GuestUrlUsage

"""
import datetime
import logging

from django.db import models
from django.core.urlresolvers import resolve, reverse

import pytz
from uuidfield import UUIDField

logger = logging.getLogger(__name__)


def now(tz=pytz.utc):
    """Return a timezone-aware timestamp."""
    return datetime.datetime.utcnow().replace(tzinfo=tz)


class GuestUrlExpired(Exception):
    """Custom exception raised when trying to use an expired link."""
    pass


class GuestUrlInvalid(Exception):
    """Custom exception raised when trying to use a link beyond max_usage."""
    pass


class GuestUrlManager(models.Manager):
    """Custom object manager for GuestUrl instances."""

    def create_guest_url(self, source_url, expires_at=None, max_uses=-1, save=True):
        """Create a new Guest instance from a source URL.

        Args:
            source_url: the source_url to initialise the GuestUrl with

        Kwargs:
            expires_at: a datetime representing the expiry time of the link.
            max_uses: an int, the maximum number of times it can be used.
            save: bool, if True then save the new instance.

        Returns a new instance.

        """
        guest_url = GuestUrl(
            source_url=source_url,
            expires_at=expires_at,
            max_uses=max_uses
        )
        if save:
            guest_url.save()

        return guest_url


class GuestUrl(models.Model):
    """The URL that is being 'guested', and any restrictions around its use.

    A GuestUrl represents a URL and any restrictions around its use - whether
    it can only be used for a period of time, or a certain number of times.

    The process of guesting a URL involves generating a new URL in a standard
    form (/link/<uuid>) that proxies the underlying URL in an anonymous way
    (to hide the original source URL). This isn't a security feature, it's a
    way of providing guest access to views that might otherwise be inaccessible
    to someone. The links can be time-bound, or usage bound (or both) - so that
    you could have a one-use only link.

    """
    uuid = UUIDField(auto=True)
    source_url = models.URLField()
    # -1 is a sentinel value indicating unlimited usage
    max_uses = models.IntegerField(default=-1)
    used_to_date = models.IntegerField(default=0)
    expires_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField()
    last_updated_at = models.DateTimeField()

    objects = GuestUrlManager()

    def __repr__(self):
        return (
            u"<GuestUrl id=%s, url='%s'>" %
            (self.id, self.source_url)
        )

    @property
    def has_expired(self):
        """Return True if we've gone past the expiry date."""
        return self.expires_at is not None and self.expires_at < now()

    @property
    def is_valid(self):
        """Evaluate the max_uses v used_to_date state."""
        return (self.max_uses < 0) or (self.used_to_date < self.max_uses)

    @property
    def can_be_used(self):
        """Return True if we haven't exceeded max_uses and haven't expired."""
        return self.is_valid and (self.has_expired is False)

    def get_absolute_url(self):
        """Returns the reverse() url."""
        return reverse('get_guest_url', kwargs={'link_uuid': str(self.uuid)})

    def save(self, *args, **kwargs):
        """Set the timestamps."""
        timestamp = now()
        self.created_at = self.created_at or timestamp
        self.last_updated_at = timestamp
        super(GuestUrl, self).save(*args, **kwargs)
        return self

    def reverse(self):
        """Returns the new 'reverse'd URL.

        This uses get_absolute_url method - and is only here as
        a standalone method to round the 'resolve' and 'reverse' methods to
        make it easier to use.

        """
        return self.get_absolute_url()

    def resolve(self):
        """Resolve the source_url into (func, args, kwargs)."""
        return resolve(self.source_url)

    def process_request(self, request):
        """Call the source_url view function and return the response.

        Args:
            request: the underlying view function will require a request
                object, so this must be passed in.

        Returns the HttpResponse object returned from the underlying view
            function.

        Raises:
            GuestUrlExpired if the URL has expired
            GuestUrlInvalid if the max_usage has been used up

        """
        assert request.method == 'GET', "Invalid request method '%s' - must be GET." % request.method  # noqa
        if self.has_expired:
            raise GuestUrlExpired()
        elif self.is_valid is False:
            raise GuestUrlInvalid()

        func, args, kwargs = self.resolve()
        response = func(request, *args, **kwargs)
        self.used_to_date = self.used_to_date + 1
        self.save()
        return response
