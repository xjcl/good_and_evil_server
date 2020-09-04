# TODO upgrade django version
# TODO use better webserver than built-in django one
# TODO rate-limit people -_-  or limit number of threads or something

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.utils.http import urlencode
from django.shortcuts import render

from . import process
from . import forms

def make_image_path(d):
    return urlencode(sorted(d.items()))

def index(request):
    return HttpResponseRedirect('create')

def create_image(request):
    '''GET: Return form to specify parameters for a GET request'''
    '''POST: Submit create_image form. Creates file with params locally'''
    if request.method == 'POST':
        form = forms.GaeParamsForm(request.POST)
        if form.is_valid():
            try:
                open(make_image_path(form.cleaned_data) + '.png', 'rb')
            except:
                hex_color = form.cleaned_data.get('hex_color')
                process.run(
                    colorLo=(int(hex_color[-6:-4], 16), int(hex_color[-4:-2], 16), int(hex_color[-2:], 16)),
                    str1=form.cleaned_data.get('str1'),
                    str2=form.cleaned_data.get('str2'),
                    fontSize=form.cleaned_data.get('font_size'),
                    getId=lambda: make_image_path(form.cleaned_data)
                )
            return HttpResponseRedirect('get?' + make_image_path(form.cleaned_data))
    else:
        form = forms.GaeParamsForm()

    return render(request, 'GaeParamsForm.html', {'form': form})

def get_image(request):
    '''Return image if it has been created through form previously'''
    try:
        with open(make_image_path(request.GET) + '.png', 'rb') as f:
            return HttpResponse(f.read(), content_type='image/png')
    except OSError:
        return HttpResponseNotFound('404 No image with specified parameters on this server.'
            '<br><br>'
            'Create one using the <a href="create">form</a>')
