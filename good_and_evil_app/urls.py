from django.conf.urls import url

from . import views

# TODO: allow commas maybe?
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<hex_color>#?[0-9a-fA-F]+),(?P<str1>[\w\s\-]*),(?P<str2>[\w\s\-]*)/$', views.detail, name='detail'),
    url(r'^(?P<hex_color>#?[0-9a-fA-F]+),(?P<str1>[\w\s\-]*),(?P<str2>[\w\s\-]*),(?P<font_size>[0-9]+)/$', views.detail, name='detail'),
]
