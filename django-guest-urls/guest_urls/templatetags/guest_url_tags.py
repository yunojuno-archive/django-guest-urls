# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.fields import DateTimeField
from django.utils import timezone

from guest_urls.models import GuestUrl

register = template.Library()


def try_parse_date(val):
    """Parse input string into a date, if possible.

    The Django DateTimeField.to_python() method parses strings, dates and datetimes
    into datetime instances - so use this to do the heavy lifting, then copy
    the Django timezone fixing from DateTimeField().get_prep_value to ensure
    that we have a timezone-aware date.

    This is a straight lift from django.db.models.fields.DateTimeField.get_prep_value,
    only without the warning message - as this contains a reference to the parent
    model of field, which doesn't work in this case.

    # See this for details:
    # https://github.com/django/django/blob/1.6.5/django/db/models/fields/__init__.py#L894-L906

    """
    value = DateTimeField().to_python(val)
    if value is not None and settings.USE_TZ and timezone.is_naive(value):
        default_timezone = timezone.get_default_timezone()
        value = timezone.make_aware(value, default_timezone)
    return value


@register.filter
def guest_url(source_url, usage=None):
    """Converts a known URL into a GuestUrl.

    Creating a guest url from a known url is easy, the magic is in the parsing
    of the usage argument. GuestUrl objects can have a rate limit and / or an
    expiry date. Template filters can only have one argument - so this single
    argument has to be parseable. The following rules apply:

    * String is split using ',' delimiter and each sub-arg is parsed
    * If the arg is an integer, then it's assumed to be max usage counter
    * If the arg can be parsed as a datetime, then it's assumed to be an expiry
    * If the arg can be parsed as a space delimited 'int string' then it's
        assumed to be a relative datetime

    TODO: the interval parsing is not yet complete.

    Examples:

        {{ '/original/url/'|guest_url }} -> unlimited, no expiry
        {{ '/original/url/'|guest_url:"1" }} -> single use, no expiry
        {{ '/original/url/'|guest_url:"1 day" }} -> unlimited, expires in one day
        {{ '/original/url/'|guest_url:"12-Jul-2014" }} -> unlimited, expires on 12-Jul-2014
        {{ '/original/url/'|guest_url:"1, 1 hour" }} -> single use, in next hour

    Args:
        source_url: a url that can be resolved back into a view function.
        usage: a string that is parsed to determine the usage (expiry, max
            uses etc.)

    Returns a new URL that maps to the input URL, but as a GuestUrl instead.
    """
    # split, strip and remove the empties
    args = [a.strip() for a in (usage or "").split(',') if len(a) > 0]
    assert len(args) < 3, "Invalid guest_url filter argument - %s" % usage

    guest_url = GuestUrl.objects.create_guest_url(source_url, save=False)

    for arg in args:

        # start off easy - try parsing out an integer as max_uses
        try:
            guest_url.max_uses = int(arg)
            continue
        except ValueError:
            pass

        # next up is a date / datetime
        try:
            expires_at = try_parse_date(arg)
            if expires_at is not None:
                # now that we've got it, remove it from the list and move on
                guest_url.expires_at = expires_at
                continue
        except ValidationError:
            pass

        # if we're still going, we have something we can't parse.
        raise ValueError("Unparseable guest_url filter arguments: %s" % arg)

    return guest_url.save().get_absolute_url()
