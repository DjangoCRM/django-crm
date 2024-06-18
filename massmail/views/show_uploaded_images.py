from django.conf import settings
from django.shortcuts import render


def show_uploaded_images(request):
    path = settings.MEDIA_ROOT / 'pics'
    files = list(path.iterdir())

    return render(request, "massmail/show_uploaded_images.html", {"files": files})
