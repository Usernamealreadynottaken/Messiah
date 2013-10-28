from datetime import date
from django.shortcuts import render
import random
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

# Zeby skorzystac z ajaxa potrzebujemy zwrocic HttpResponse object.
# Jesli korzystamy ze skrotu ajax po prostu zwraca error.
from django.http import HttpResponse, Http404

# Nasze modele
from Hotel.models import Usluga, Pokoj, Rezerwacja, OpisHotelu, PokojNaRezerwacji, UslugaNaRezerwacji, Wiadomosc, KategoriaJedzenia, Jedzenie


@login_required
def wiadomosci(request):
    return render(request, 'hotel/wiadomosci.html', {'wiadomosci': Wiadomosc.objects.all()})


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

def cennik(request):
    uslugi_wewnetrzne = Usluga.objects.filter(zewnetrzna=False)
    uslugi_zewnetrzne = Usluga.objects.filter(zewnetrzna=True)
    return render(request, 'hotel/cennik.html', {
        'kategorie': KategoriaJedzenia.objects.all(),
        'jedzenie': Jedzenie.objects.all(),
        'uslugi_wewnetrzne': uslugi_wewnetrzne,
        'uslugi_zewnetrzne': uslugi_zewnetrzne
    })


def kod_rezerwacji():
    # Najpierw zbierzmy wszystkie kody jakie zostaly juz przydzielone
    kody = []
    for r in Rezerwacja.objects.all():
        kody.append(r.kod)

    symbols = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    kod = ''
    while True:
        for i in range(0, 12):
            kod += random.choice(symbols)
        if not kod in kody:
            break

    return kod


# Widok do wykonania rezerwacji
# Sprawdza czy zaznaczone przez uzytkownika pokoje/liczba osob w ogole mozna wynajac
# i jesli mozna to tworzy w bazie danych odpowiednia rezerwacje
def rezerwacje_wyslij(request):
    response_message = 'success'
    try:
        test_post = request.POST['name']

        # Pewne rzeczy POST przekazuje w stringu wiec musimy je skonwertowac
        # Daty
        poczatek_pobytu_split = request.POST['date-from'].split('/')
        koniec_pobytu_split = request.POST['date-to'].split('/')
        poczatek_pobytu = date(int(poczatek_pobytu_split[2]), int(poczatek_pobytu_split[0]), int(poczatek_pobytu_split[1]))
        koniec_pobytu = date(int(koniec_pobytu_split[2]), int(koniec_pobytu_split[0]), int(koniec_pobytu_split[1]))

        # Ilosc pokojow
        ilosc_pokojow = int(request.POST['rooms'])

        # Ilosc doroslych i dzieci w pokojach
        dorosli = []
        dzieci = []
        for i in range(1, ilosc_pokojow + 1):
            dorosli.append(int(request.POST['adults%d' % (i,)]))
            dzieci.append(int(request.POST['kids%d' % (i,)]))

        # Chcemy sprawdzic czy wybrane pokoje sa dostepne. Do tego potrzebujemy dat (sa wyzej)
        # oraz specjalnie przygotowanego slownika
        wymagane_pokoje = {'ilosc': ilosc_pokojow}
        for i in range(1, ilosc_pokojow + 1):
            wymagane_pokoje['pokoj%d' % (i,)] = dorosli[i-1] + dzieci[i-1]

        # Funckja ktora jest rowniez wykorzystywana do ajaxa zwraca liste statusow, czyli pk
        # jesli pokoj jest wolny, jesli nie to status z bledem (string)
        list_of_pks_str = wyszukaj_pokoje(poczatek_pobytu, koniec_pobytu, wymagane_pokoje)

        # Mozemy stworzyc rezerwacje tylko jesli otrzymalismy pk dla wszystkich zamawianych pokojow
        try:
            list_of_pks = []
            for i in range(1, ilosc_pokojow + 1):
                list_of_pks.append(int(list_of_pks_str['pokoj%d' % (i,)]))

            # Tworzymy liste pk zamowionych uslug
            uslugi = []
            for k, v in request.POST.items():
                if k.startswith('in') or k.startswith('out'):
                    uslugi.append(int(v))

            # Pozostale rzeczy mozemy po prostu przepisac z POSTa do rezerwacji
            # Teraz tworzymy instancje wszystkich klas po kolei
            # Rezerwacja
            cena_dorosly = OpisHotelu.objects.filter()[0].cena_dorosly
            cena_dziecko = OpisHotelu.objects.filter()[0].cena_dziecko
            nowa_rezerwacja = Rezerwacja(poczatek_pobytu=poczatek_pobytu,
                                         koniec_pobytu=koniec_pobytu,
                                         email=request.POST['email'],
                                         telefon=request.POST['tel'],
                                         nazwisko=request.POST['name'],
                                         dodatkowe_instrukcje=request.POST['requests'],
                                         kod=kod_rezerwacji(),
                                         cena_dorosly=cena_dorosly,
                                         cena_dziecko=cena_dziecko)
            nowa_rezerwacja.save()

            # PokojNaRezerwacji
            for i in range(0, ilosc_pokojow):
                nowy_pnr = PokojNaRezerwacji(rezerwacja=nowa_rezerwacja,
                                             pokoj=Pokoj.objects.get(pk=list_of_pks[i]),
                                             doroslych=dorosli[i],
                                             dzieci=dzieci[i],
                                             cena=Pokoj.objects.get(pk=list_of_pks[i]).cena)
                nowy_pnr.save()

            # UslugaNaRezerwacji
            # Tylko w sytuacji, gdy zostaly wybrane jakies uslugi
            for u in uslugi:
                nowa_unr = UslugaNaRezerwacji(rezerwacja=nowa_rezerwacja,
                                              usluga=Usluga.objects.get(pk=u),
                                              cena=0)
                nowa_unr.save()

        # Ten ValueError zostanie zwrocony jezeli probojemy zarezerwowac pokoje w momencie kiedy
        # funkcja sprawdzajaca dostepnosc zwrocila inne wiadomosci niz same pk pokojow
        except ValueError:
            response_message = 'validation_error'

    except ValueError:
        response_message = 'site_error'

    except KeyError:
        # Nie zostal przekazany POST
        raise Http404

    response = '{"message": "' + response_message + '"'
    if response_message == 'success':
        response += ', "kod": "' + nowa_rezerwacja.kod + '"'
    response += '}'
    return HttpResponse(response)


# Ta funkcja sama w sobie to nie jest view
# Jest to funkcja pomocnicza do sprawdzania czy zaznaczone pokoje sa dostepne
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

             # Stworzmy liste pk pokojow o odpowiednim rozmiarze
            viable_rooms = []
            for p in Pokoj.objects.all():
                if p.rozmiar == wymagane_pokoje[pokoj_i]:
                    viable_rooms.append(p.pk)

            # Lecimy po rezerwacjach i jezeli istnieje taka rezerwacja ze w podanej dacie pokoj
            # jest zajety to usuwamy go z listy
            rooms_to_remove = []
            for room in viable_rooms:
                for r in Rezerwacja.objects.all():
                    if poczatek_pobytu <= r.poczatek_pobytu <= koniec_pobytu or \
                            koniec_pobytu >= r.koniec_pobytu >= poczatek_pobytu or \
                            r.poczatek_pobytu <= poczatek_pobytu <= r.koniec_pobytu:
                        if r.pokojnarezerwacji_set.filter(pokoj__pk=room):
                            rooms_to_remove.append(room)
                            break

            # Usuwamy znalezione zajete pokoje
            for room in rooms_to_remove:
                try:
                    viable_rooms.remove(room)
                except ValueError:
                    pass

            # Do tego trzeba usunac wszystkie pokoje ktore juz sa na liscie zwracanej
            for key, value in return_status.items():
                try:
                    rpk = int(value)
                    viable_rooms.remove(rpk)
                except ValueError:
                    pass

            # Jesli zostaly nam jakies wolne pokoje to mozna pierwszy zwrocic jako wolny
            if len(viable_rooms) > 0:
                return_status[pokoj_i] = viable_rooms[0]
            else:
                return_status[pokoj_i] = 'no_free_rooms'

    return return_status


# Ten widok obsluguje zapytanie asynchroniczne w momencie wybierania pokojow/ilosci osob
# i sprawdza czy zaznaczone przez uzytkownika pokoje w ogole mozna wynajac
def rezerwacje_sprawdz(request):
    if request.is_ajax():
        try:
            # Konwersja dat ze stringow do date
            poczatek_pobytu_split = request.GET['poczatekPobytu'].split('/')
            koniec_pobytu_split = request.GET['koniecPobytu'].split('/')
            poczatek_pobytu = date(int(poczatek_pobytu_split[2]),
                                   int(poczatek_pobytu_split[0]),
                                   int(poczatek_pobytu_split[1]))
            koniec_pobytu = date(int(koniec_pobytu_split[2]),
                                 int(koniec_pobytu_split[0]),
                                 int(koniec_pobytu_split[1]))
            # Slownik z wymaganymi rozmiarami pokojow
            wymagane_pokoje = {'ilosc': int(request.GET['iloscPokojow'])}
            dorosli_dzieci = {}
            for i in range(1, wymagane_pokoje['ilosc'] + 1):
                dorosli = int(request.GET['dorosli%d' % (i,)])
                dzieci = int(request.GET['dzieci%d' % (i,)])
                wymagane_pokoje['pokoj%d' % (i,)] = dorosli + dzieci
                dorosli_dzieci['dorosli%d' % (i,)] = dorosli
                dorosli_dzieci['dzieci%d' % (i,)] = dzieci

            list_of_pks = wyszukaj_pokoje(poczatek_pobytu, koniec_pobytu, wymagane_pokoje)

            # Tworzymy JSON zawierajacy statusy wszyskich pokojow
            response = '{'
            for i in range(1, wymagane_pokoje['ilosc'] + 1):
                response += '"pokoj%d": "%s", ' % (i, str(list_of_pks['pokoj%d' % (i,)]))

            # Dodajemy do JSONa koszt wynajecia pokoju na tyle dni
            cena_dorosly = OpisHotelu.objects.filter()[0].cena_dorosly
            cena_dziecko = OpisHotelu.objects.filter()[0].cena_dziecko
            ile_dni = (koniec_pobytu - poczatek_pobytu).days + 1
            cena = 0
            for i in range(1, wymagane_pokoje['ilosc'] + 1):
                try:
                    p = Pokoj.objects.get(pk=int(list_of_pks['pokoj%d' % (i,)]))
                    cena += p.cena * ile_dni
                    cena += cena_dorosly * ile_dni * dorosli_dzieci['dorosli%d' % (i,)]
                    cena += cena_dziecko * ile_dni * dorosli_dzieci['dzieci%d' % (i,)]
                except ValueError:
                    pass

            response += '"cena": "%d"}' % (cena,)

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


# Widok do ajaxa sprawdzajacego czy rezerwacja o podanym numerze rezerwacji istnieje
def rezerwacje_sprawdz_kod(request, code):
    if request.is_ajax():
        try:
            requested_res = Rezerwacja.objects.get(kod=code)
            response = "true"
        except ObjectDoesNotExist:
            response = "false"
        return HttpResponse(response)
    else:
        raise Http404


def rezerwacje_kod(request, code):
    try:
        requested_res = Rezerwacja.objects.get(kod=code)

        # Daty wyswietlane na stronie maja inny format niz __unicode__ clasy data
        # wiec trzeba przekonwertowac
        dzien = str(requested_res.poczatek_pobytu.day)
        if len(dzien) == 1:
            dzien = '0' + dzien
        miesiac = str(requested_res.poczatek_pobytu.month)
        if len(miesiac) == 1:
            miesiac = '0' + miesiac
        poczatek_pobytu = '%s/%s/%d' % (miesiac, dzien, requested_res.poczatek_pobytu.year,)

        dzien = str(requested_res.koniec_pobytu.day)
        if len(dzien) == 1:
            dzien = '0' + dzien
        miesiac = str(requested_res.koniec_pobytu.month)
        if len(miesiac) == 1:
            miesiac = '0' + miesiac
        koniec_pobytu = '%s/%s/%d' % (miesiac, dzien, requested_res.koniec_pobytu.year,)
        print koniec_pobytu

        # Liczba pokoi
        liczba_pokoi = PokojNaRezerwacji.objects.filter(rezerwacja=requested_res).count()

        # Lista uslug ktore sa na tej rezerwacji
        uslugi = []
        for unr in UslugaNaRezerwacji.objects.filter(rezerwacja=requested_res):
            uslugi.append(unr.usluga.pk)

        # Lista uslug jest potrzebna zeby w ogole wyrenderowac strone
        uslugi_wewnetrzne = Usluga.objects.filter(zewnetrzna=False)
        uslugi_zewnetrzne = Usluga.objects.filter(zewnetrzna=True)

        return render(request, 'hotel/rezerwacje.html', {
            'uslugi_all': Usluga.objects.all(),
            'uslugi_wewnetrzne': uslugi_wewnetrzne,
            'uslugi_zewnetrzne': uslugi_zewnetrzne,
            'rezerwacja_do_edycji': requested_res,
            'poczatek_pobytu': poczatek_pobytu,
            'koniec_pobytu': koniec_pobytu,
            'liczba_pokoi': liczba_pokoi,
            'uslugi': uslugi
        })

    except ObjectDoesNotExist:
        raise Http404