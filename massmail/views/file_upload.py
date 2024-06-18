from django import forms
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

allowed_extensions = ['jpg', 'png', 'gif']
help_text_str = _("Allowed file extensions: ") + f" {', '.join(allowed_extensions)}"


def validate_image_file_extension(value):
    return FileExtensionValidator(
        allowed_extensions=allowed_extensions
    )(value)


class UploadFileForm(forms.Form):
    file = forms.FileField(
        validators=[validate_image_file_extension],
        help_text=help_text_str
    )


def file_upload(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            path = settings.MEDIA_ROOT / 'pics' / file.name
            with open(path, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            return HttpResponse(
                '<script type="text/javascript">window.close()</script>'
            )
    else:
        form = UploadFileForm()

    return render(request, "massmail/pic_upload.html", {"form": form})
