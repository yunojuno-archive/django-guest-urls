# -*- coding: utf-8 -*-
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseGone
)


def test_link_args_0(request):
    """Basic GET request, no args, no kwargs."""
    return HttpResponse("OK")


def test_link_args_1(request, year):
    """Basic GET request, one arg."""
    return HttpResponse("OK")


def test_link_args_2(request, year, month):
    """Basic GET request, two args."""
    return HttpResponse("OK")


def test_link_kwargs_1(request, year=0):
    """Basic GET request, one kwarg."""
    return HttpResponse("OK")


def test_link_kwargs_2(request, year=0, month=0):
    """Basic GET request, two kwargs."""
    return HttpResponse("OK")
