# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include

# taken from the django docs ;-)
urlpatterns = patterns(
    'test_app.views',
    url(r'^articles/$', 'test_link_args_0', name='test_link_args_0'),
    url(r'^articles/([0-9]{4})/$',
        'test_link_args_1', name='test_link_args_1'),
    url(r'^articles/([0-9]{4})/([0-9]{2})/$',
        'test_link_args_2', name='test_link_args_2'),
    url(r'^articles/(?P<year>[0-9]{4})/$',
        'test_link_kwargs_1', name="test_link_kwargs_1"),
    url(r'^articles/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$',
        'test_link_kwargs_2', name='test_link_kwargs_2'),
    url(r'^', include('guest_urls.urls')),
)
