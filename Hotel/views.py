import datetime
from datetime import date
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Zeby skorzystac z ajaxa potrzebujemy zwrocic HttpResponse object.
# Jesli korzystamy ze skrotu ajax po prostu zwraca error.
from django.http import HttpResponse, Http404

from Hotel.models import Usluga, Pokoj, PokojNaRezerwacji, Rezerwacja


@login_required
def wiadomosci(request):
    return render(request, 'hotel/wiadomosci.html')


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


def wyszukaj_pokoje(poczatek_pobytu, koniec_pobytu, wymagane_pokoje):
    return_status = {'pokoj1': 'not_checked', 'pokoj2': 'not_checked', 'pokoj3': 'not_checked'}

    # Maksymalna pojemnosc pokoju
    max_room_capacity = 0
    for p in Pokoj.objects.all():
        if p.rozmiar > max_room_capacity:
            max_room_capacity = p.rozmiar

    for i in range(1, wymagane_pokoje['ilosc'] + 1):
        pokoj_i = 'pokoj%d' % (i,)

        # Jesli pokoj ma 0 osob lub wiecej niz najwiekszy pokoj w hotelu
        # zaznaczamy odpowiedni status
        if wymagane_pokoje[pokoj_i] <= 0:
            return_status[pokoj_i] = 'zero_selected'
        elif wymagane_pokoje[pokoj_i] > max_room_capacity:
            return_status[pokoj_i] = 'over_max_capacity'

        # Pokoj ma normalna ilosc osob, szukamy czy jest wolny
        else:

            print 'POKOJ %d' % (i,)

             # Stworzmy liste pk pokojow o odpowiednim rozmiarze
            viable_rooms = []
            for p in Pokoj.objects.all():
                print '  iter pokoj %d' % (p.pk,)
                if p.rozmiar == wymagane_pokoje[pokoj_i]:
                    print '    viable_rooms + %d' % (p.pk,)
                    viable_rooms.append(p.pk)

            vr_print = ''
            for room in viable_rooms:
                vr_print += '%d, ' % (room,)
            print vr_print

            # Lecimy po rezerwacjach i jezeli istnieje taka rezerwacja ze w podanej dacie pokoj
            # jest zajety to usuwamy go z listy
            rooms_to_remove = []
            for room in viable_rooms:
                print '  iter viable_rooms %d' % (room,)
                for r in Rezerwacja.objects.all():
                    print '    iter reservation %s' % (r.email,)
                    if poczatek_pobytu <= r.poczatek_pobytu <= koniec_pobytu or \
                            koniec_pobytu >= r.koniec_pobytu >= poczatek_pobytu or \
                            r.poczatek_pobytu <= poczatek_pobytu <= r.koniec_pobytu:
                        print '      date collide'
                        if r.pokojnarezerwacji_set.filter(pokoj__pk=room):
                            print '      res collide with %d' % (room,)
                            rooms_to_remove.append(room)

            # Usuwamy znalezione zajete pokoje
            for room in rooms_to_remove:
                try:
                    viable_rooms.remove(room)
                except KeyError:
                    pass

            # Do tego trzeba usunac wszystkie pokoje ktore juz sa na liscie zwracanej
            for key, value in return_status.items():
                try:
                    rpk = int(value)
                    try:
                        viable_rooms.remove(rpk)
                    except KeyError:
                        pass
                except ValueError:
                    pass

            # Jesli zostaly nam jakies wolne pokoje to mozna pierwszy zwrocic jako wolny
            if len(viable_rooms) > 0:
                return_status[pokoj_i] = viable_rooms[0]
            else:
                return_status[pokoj_i] = 'no_free_rooms'

    return return_status


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
            for i in range(1, wymagane_pokoje['ilosc'] + 1):
                wymagane_pokoje['pokoj%d' % (i,)] = int(request.GET['dorosli%d' % (i,)]) + int(request.GET['dzieci%d' % (i,)])

            # Tymczasowy wynik
            list_of_pks = wyszukaj_pokoje(poczatek_pobytu, koniec_pobytu, wymagane_pokoje)

            response = '{'
            for i in range(1, wymagane_pokoje['ilosc'] + 1):
                if i > 1:
                    response += ', '
                response += '"pokoj%d": "%s"' % (i, str(list_of_pks['pokoj%d' % (i,)]))
            response += '}'

        # Czegos brakuje w requescie
        except KeyError, key:
            response = key

        # Cos w requescie ma nieprawidlowy typ
        except SyntaxError:
            response = 'Parse error'

        # Nieprawidlowy format, np data 10/1234/2013
        except ValueError, value:
            response = value

        return HttpResponse(response)
    else:
        raise Http404