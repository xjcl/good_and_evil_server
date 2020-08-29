# TODO upgrade django version
# TODO use better webserver than built-in django one
# TODO rate-limit people -_-  or limit number of threads or something

from django.http import HttpResponse
from . import process

def index(request):
    return HttpResponse("TODO you can make requests or something")

# TODO reuqest cache (or just use HDD)
def detail(request, hex_color, str1, str2, font_size=70):
    img_path = process.run(
        colorLo=(int(hex_color[-6:-4], 16), int(hex_color[-4:-2], 16), int(hex_color[-2:], 16)),
        str1=str1,
        str2=str2,
        fontSize=int(font_size)
    )

    with open(img_path, "rb") as f:
        return HttpResponse(f.read(), content_type="image/png")
