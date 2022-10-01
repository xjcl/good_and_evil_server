from django.conf.urls import url

from . import views

# TODO: allow commas maybe?
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^get$', views.get_image, name='get'),
    url(r'^create$', views.create_image, name='create'),
    url(r'^preview$', views.create_preview, name='preview'),
]
