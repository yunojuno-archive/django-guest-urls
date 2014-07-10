from django.conf.urls import patterns, url

urlpatterns = patterns(
    'guest_urls.views',
    url(
        r'^link/(?P<link_uuid>[a-zA-Z0-9\+\/\_\=]{1,32})/$',
        'get_guest_url',
        name='get_guest_url'
    ),
)
