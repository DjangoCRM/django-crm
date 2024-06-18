from django.http.response import HttpResponse


def debug(request):
    """
    Use this view for debug.
    It's available at address: <home page>debug/
    """

    msg = 'Done for ...'
    return HttpResponse(msg)
