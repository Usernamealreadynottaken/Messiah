from django.shortcuts import render

# Temporary, for testing ajax
from django.http import HttpResponse, Http404


def glowna(request):
    return render(request, "hotel/index.html")


def rezerwacje(request):
    return render(request, "hotel/rezerwacje.html")


def rezerwacje_check(request):
    if request.is_ajax():
        try:
            pokoj = int(request.GET['pokoj'])
        except KeyError:
            return HttpResponse('Brak pokoju')
        return HttpResponse('Some string')
    else:
        raise Http404