from common.models import TheFile


def copy_files(obj_from, obj_to):

    for f in obj_from.files.all():
        TheFile.objects.create(
            file=f.file,
            content_object=obj_to
        )
