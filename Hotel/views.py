import datetime
from datetime import date
from django.shortcuts import render

# Zeby skorzystac z ajaxa potrzebujemy zwrocic HttpResponse object.
# Jesli korzystamy ze skrotu ajax po prostu zwraca error.
from django.http import HttpResponse, Http404

from Hotel.models import Usluga, Pokoj


def glowna(request):
    return render(request, 'hotel/index.html')


def rezerwacje(request):
    uslugi_wewnetrzne = Usluga.objects.filter(zewnetrzna=False)
    uslugi_zewnetrzne = Usluga.objects.filter(zewnetrzna=True)
    return render(request, 'hotel/rezerwacje.html', {
        'uslugi_all': Usluga.objects.all(),
        'uslugi_wewnetrzne': uslugi_wewnetrzne,
        'uslugi_zewnetrzne': uslugi_zewnetrzne
    })


def rezerwacje_check(request):
    if request.is_ajax():

        try:
            # Konwersja dat ze stringow do date
            poczatek_pobytu_split = request.GET['poczatekPobytu'].split('/')
            koniec_pobytu_split = request.GET['koniecPobytu'].split('/')
            poczatek_pobytu = date(int(poczatek_pobytu_split[2]), int(poczatek_pobytu_split[0]), int(poczatek_pobytu_split[1]))
            koniec_pobytu = date(int(koniec_pobytu_split[2]), int(koniec_pobytu_split[0]), int(koniec_pobytu_split[1]))

            # Slownik z wymaganymi rozmiarami pokojow
            wymagane_pokoje = {'ilosc': int(request.GET['iloscPokojow'])}
            dostepne_pokoje = {}
            for i in range(1, wymagane_pokoje['ilosc'] + 1):
                wymagane_pokoje['pokoj%d' % (i,)] = int(request.GET['dorosli%d' % (i,)]) + int(request.GET['dzieci%d' % (i,)])
                dostepne_pokoje['pokoj%d' % (i,)] = False

            # Szukamy czy pokoje o wymaganych rozmiarach sa w bazie
            for i in range(1, wymagane_pokoje['ilosc'] + 1):
                for p in Pokoj.objects.all():
                    if p.rozmiar == wymagane_pokoje['pokoj%d' % (i,)]:
                        dostepne_pokoje['pokoj%d' % (i,)] = True
                        break

            # Tymczasowy wynik
            response = ''
            sample_list = []
            sample_list.append(1)
            sample_list.append(2)
            for l in sample_list:
                response += '%d, ' % l

        # Czegos brakuje w requescie
        except KeyError:
            response = 'Dict error'

        # Cos w requescie ma nieprawidlowy typ
        except SyntaxError:
            response = 'Parse error'

        # Nieprawidlowy format, np data 10/1234/2013
        except ValueError:
            response = 'Value error'

        return HttpResponse(response)
    else:
        raise Http404