from django.shortcuts import render

# Zeby skorzystac z ajaxa potrzebujemy zwrocic HttpResponse object.
# Jesli korzystamy ze skrotu ajax po prostu zwraca error.
from django.http import HttpResponse, Http404
from django.template import loader, RequestContext

from Hotel.models import Pokoj


def glowna(request):
    return render(request, 'hotel/index.html')


def rezerwacje(request):
    return render(request, 'hotel/rezerwacje.html', {'pokoje': Pokoj.objects.all()})


def rezerwacje_check(request):
    if request.is_ajax():
        # Ten sam template jest zwracany niezaleznie czy byl blad czy nie
        template = loader.get_template('hotel/rezerwacje_message.html')

        response = {}
        try:
            pokoj = int(request.GET['pokoj'])
            response['pokoj'] = pokoj
        except ValueError:
            response['error_message'] = 'Brak zaznaczonych pokojow'

        context = RequestContext(request, response)
        return HttpResponse(template.render(context))
    else:
        raise Http404