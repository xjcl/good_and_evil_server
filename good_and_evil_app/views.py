# TODO upgrade django version
# TODO use better webserver than built-in django one
# TODO rate-limit people -_-  or limit number of threads or something
import glob
import os
import base64

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponseBadRequest
from django.utils.http import urlencode
from django.shortcuts import render

from . import process
from . import forms

def _make_image_path(d):
    return urlencode(sorted(d.items()))

def index(request):
    return HttpResponseRedirect('create')

def _create_image(form, preview=False):
    hex_color = form.cleaned_data.get('hex_color')
    process.run(
        size=250 if preview else 720,
        get_id=lambda: _make_image_path(form.cleaned_data),
        color_dark=(int(hex_color[-6:-4], 16), int(hex_color[-4:-2], 16), int(hex_color[-2:], 16)),
        str1=form.cleaned_data.get('str1'),
        str2=form.cleaned_data.get('str2'),
        font_size=(form.cleaned_data.get('font_size') * (250 if preview else 720))//720,
    )

def create_image(request):
    '''GET: Return form to specify parameters for a GET request'''
    '''POST: Submit create_image form. Creates file with params locally'''
    if request.method == 'POST':
        form = forms.GaeParamsForm(request.POST)
        if form.is_valid():
            if not os.path.exists(_make_image_path(form.cleaned_data) + '.png'):
                _create_image(form)
            return HttpResponseRedirect('get?' + _make_image_path(form.cleaned_data))
    else:
        form = forms.GaeParamsForm()

    return render(request, 'GaeParamsForm.html', {'form': form})

def create_preview(request):
    form = forms.GaeParamsForm(request.GET)

    if not form.is_valid():
        return HttpResponseBadRequest('cannot create preview for given form data')

    img_path = _make_image_path(form.cleaned_data) + '.png'

    if not os.path.exists(img_path):
        _create_image(form, preview=True)

        with open(img_path, 'rb') as f:
            data = f.read()

        for filename in glob.glob(_make_image_path(form.cleaned_data) + '*'):
            os.remove(filename)  # do not save previews (3 per request)
    else:
        # might have the full 720p image already stored so do not remove it
        with open(img_path, 'rb') as f:
            data = f.read()

    return HttpResponse(base64.encodebytes(data))

def get_image(request):
    '''Return image if it has been created through form previously'''
    try:
        with open(_make_image_path(request.GET) + '.png', 'rb') as f:
            return HttpResponse(f.read(), content_type='image/png')
    except OSError:
        return HttpResponseNotFound('404 No image with specified parameters on this server.'
            '<br><br>'
            'Create one using the <a href="create">form</a>')
