import random
import datetime
from datetime import date
from django.core.mail.message import EmailMessage
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.core import mail
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect

# Zeby skorzystac z ajaxa potrzebujemy zwrocic HttpResponse object.
# Jesli korzystamy ze skrotu ajax po prostu zwraca error.
#
# Ok okazuje sie ze powyzsze to nie prawda i jakos teraz mi dziala
# jak zwracam ajaxowi sam render
from django.http import HttpResponse, Http404

# Nasze modele
from Hotel.models import Usluga, Pokoj, Rezerwacja, OpisHotelu, PokojNaRezerwacji, UslugaNaRezerwacji, Wiadomosc, KategoriaJedzenia, Jedzenie, \
    ZdjeciaPokojow, CenaPokoju, ZdjeciaHotelu, Newsletter


# FUNKCJE (NIE-WIDOKI)

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


def kod_newsletter():
    # Najpierw zbierzmy wszystkie kody jakie zostaly juz przydzielone
    kody = []
    for r in Newsletter.objects.all():
        kody.append(r.news_kod)

    symbols = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    kod = ''
    while True:
        for i in range(0, 12):
            kod += random.choice(symbols)
        if not kod in kody:
            break

    return kod


# Ta funkcja sama w sobie to nie jest view
# Jest to funkcja pomocnicza do sprawdzania czy zaznaczone pokoje sa dostepne
def wyszukaj_pokoje(poczatek_pobytu, koniec_pobytu, wymagane_pokoje, kod=''):
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

        # Czy istnieje w bazie cena dla tego pokoju
        elif not CenaPokoju.objects.filter(rozmiar=wymagane_pokoje[pokoj_i]):
            return_status[pokoj_i] = 'no_free_rooms'

        # Pokoj ma normalna ilosc osob, szukamy czy jest wolny
        else:

            # Stworzmy liste pk pokojow o odpowiednim rozmiarze
            viable_rooms = []
            for p in Pokoj.objects.filter(dostepnosc=True):
                if p.rozmiar == wymagane_pokoje[pokoj_i]:
                    viable_rooms.append(p.pk)

            # Lecimy po rezerwacjach i jezeli istnieje taka rezerwacja ze w podanej dacie pokoj
            # jest zajety to usuwamy go z listy
            rooms_to_remove = []
            if kod:
                rezerwacje_filtered = Rezerwacja.objects.filter(~Q(kod=kod))
            else:
                rezerwacje_filtered = Rezerwacja.objects.all()
            for room in viable_rooms:
                for r in rezerwacje_filtered:
                    if poczatek_pobytu <= r.poczatek_pobytu < koniec_pobytu or \
                            koniec_pobytu >= r.koniec_pobytu > poczatek_pobytu or \
                            r.poczatek_pobytu <= poczatek_pobytu < r.koniec_pobytu:
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


def include_header_footer(context={}):
    try:
        oh = OpisHotelu.objects.filter()[0]

        logo_rozmiar = ''
        if oh.uklad == 'DD' or oh.uklad == 'DG':
            logo_rozmiar = 'logo-duze'
        else:
            logo_rozmiar = 'logo-male'

        tekst_polozenie = ''
        if oh.uklad == 'ML':
            tekst_polozenie = 'tekst-lewa'
        elif oh.uklad == 'MP':
            tekst_polozenie = 'tekst-prawa'
        elif oh.uklad == 'DD':
            tekst_polozenie = 'tekst-dol'
        elif oh.uklad == 'DG':
            tekst_polozenie = 'tekst-gora'

        hf = {'header_logo': oh.logo, 'header_logo_rozmiar': logo_rozmiar, 'header_tekst': oh.tekst_logo, 'header_tekst_polozenie': tekst_polozenie,
              'header_tekst_widoczny': oh.tekst_logo_widoczny, 'header_uklad': oh.uklad, 'footer_adres': oh.adres, 'footer_telefon': oh.telefon,
              'footer_email': oh.email}
        return dict(context, **hf)
    except IndexError:
        return context


# WIDOKI

@login_required
def biuletyn(request):
    return render(request, 'hotel/newsletter.html', {})


@login_required
def wiadomosci(request):
    return render(request, 'hotel/wiadomosci.html', {'wiadomosci': Wiadomosc.objects.all().order_by('wyslano_odpowiedz', 'data')})


@login_required
def archiwum(request):
    rez = Rezerwacja.objects.filter(Q(zarchiwizowany=True) | Q(koniec_pobytu__lte=datetime.date.today()))
    rez = rez.order_by('-koniec_pobytu')
    return render(request, 'hotel/archiwum.html', {'rezerwacje': rez})


def glowna(request):
    opis_hotelu = OpisHotelu.objects.filter()[0].opis_hotelu
    zdjecie = OpisHotelu.objects.filter()[0].zdjecie
    zdjecia_hotelu = ZdjeciaHotelu.objects.all()
    context = {
        'opis_hotelu': opis_hotelu,
        'zdjecie': zdjecie,
        'zdjecia_hotelu': zdjecia_hotelu
    }
    return render(request, 'hotel/index.html', include_header_footer(context))


def wizualizacja(request):
    class PokojeWizualizacja:
        zdjecie = None
        zajety = False

        def __init__(self, pokoj):
            self.pokoj = pokoj
            zp = ZdjeciaPokojow.objects.filter(pokoj=pokoj)
            if zp:
                self.zdjecie = zp[0].zdjecie

            dzisiaj = datetime.date.today()
            for r in Rezerwacja.objects.all():
                    if r.poczatek_pobytu <= dzisiaj < r.koniec_pobytu:
                        if r.pokojnarezerwacji_set.filter(pokoj__pk=pokoj.pk):
                            self.zajety = True
                            break

    rozmiary = []
    pokoje = []
    for p in Pokoj.objects.all():
        pokoje.append(PokojeWizualizacja(p))
        if p.rozmiar not in rozmiary:
            rozmiary.append(p.rozmiar)

    context = {'pokoje': pokoje,
               'rozmiary': sorted(rozmiary)}

    return render(request, 'hotel/wizualizacja.html', include_header_footer(context))


def wizualizacja_galeria(request, pk):
    if request.is_ajax():
        try:
            zdjecia = ZdjeciaPokojow.objects.filter(pokoj=Pokoj.objects.get(pk=pk))
            return render(request, 'hotel/wizualizacja_galeria.html', {'zdjecia': zdjecia})
        except ObjectDoesNotExist:
            raise Http404
    else:
        raise Http404


def rezerwacje(request):
    uslugi_wewnetrzne = Usluga.objects.filter(zewnetrzna=False)
    uslugi_zewnetrzne = Usluga.objects.filter(zewnetrzna=True)
    return render(request, 'hotel/rezerwacje.html', include_header_footer({
        'uslugi_all': Usluga.objects.all(),
        'uslugi_wewnetrzne': uslugi_wewnetrzne,
        'uslugi_zewnetrzne': uslugi_zewnetrzne
    }))


def cennik(request):
    uslugi_wewnetrzne = Usluga.objects.filter(zewnetrzna=False)
    uslugi_zewnetrzne = Usluga.objects.filter(zewnetrzna=True)

    return render(request, 'hotel/cennik.html', include_header_footer({
        'kategorie': KategoriaJedzenia.objects.all(),
        'jedzenie': Jedzenie.objects.all(),
        'uslugi_wewnetrzne': uslugi_wewnetrzne,
        'uslugi_zewnetrzne': uslugi_zewnetrzne,
        'cena_dorosly': OpisHotelu.objects.filter()[0].cena_dorosly,
        'cena_dziecko': OpisHotelu.objects.filter()[0].cena_dziecko,
        'ceny_pokojow': CenaPokoju.objects.all().order_by('rozmiar')
    }))


def kontakt(request):

    return render(request, 'hotel/kontakt.html', include_header_footer({
        'skype': OpisHotelu.objects.filter()[0].skype,
        'gadu': OpisHotelu.objects.filter()[0].gadu_gadu,
        'email': OpisHotelu.objects.filter()[0].email,
        'facebook': OpisHotelu.objects.filter()[0].facebook,
        'twitter': OpisHotelu.objects.filter()[0].twitter,
        'wyswietlaj_mape': OpisHotelu.objects.filter()[0].wyswietlaj_mape,
        'html_mapy_google': OpisHotelu.objects.filter()[0].html_mapy_google,
        'telefon': OpisHotelu.objects.filter()[0].telefon,
        'adres': OpisHotelu.objects.filter()[0].adres
    }))


#Zapisanie sie na newsletter przez zainteresowane osoby
def newsletter(request):
    if request.is_ajax():
        response_message = "success"
        try:
            if Newsletter.objects.filter(news_email=request.GET['email']).count():
                response_message = "already_signed"
            else:
                nowy_email = Newsletter(news_email=request.GET['email'],
                                        news_kod=kod_newsletter())
                nowy_email.save()

        except ValueError:
            response_message = "site_error"

        except KeyError:
            raise Http404

        return HttpResponse(response_message)

    else:
        raise Http404


def newsletter_anuluj(request, code):
    try:
        subscription = Newsletter.objects.get(news_kod=code)
        if subscription:
            subscription.delete()
            return render(request, 'hotel/newsletter_anuluj.html', include_header_footer())

        else:
            raise Http404#zwraca?
    except ObjectDoesNotExist:
            raise Http404


#Wysylaie biuletynu do chetnych osob ze strony admina .do zmiany.
def wyslij_biuletyn(request):
    if request.is_ajax():
        subscribers = Newsletter.objects.all()
        response_message = "success"
        from_email = 'hotel.messiah@gmail.com'
        connection = mail.get_connection()
        connection.open()
        subject = 'Hotel Messiah Newsletter!'


        for subscriber in subscribers:
            try:
                message_html = request.GET['message']+"<a href='"+request.build_absolute_uri(reverse('hotel:newsletter_anuluj', args=[subscriber.news_kod]))+"'>"+"Anuluj newsletter"+"</a>"
                to_email = subscriber.news_email
                #to_email_bcc = Newsletter.objects.values_list('news_email', flat=True)
                if subject and message_html and from_email:
                    try:
                        msg = EmailMessage(subject, message_html, from_email, [to_email])
                        msg.content_subtype = "html"
                        msg.send()
                    except KeyError:
                        response_message = "site_error"
                else:
                    response_message = "empty_field"

            except KeyError:
                raise Http404

        connection.close()
        return HttpResponse(response_message)
    else:
        raise Http404


# Wysylanie wiadomosci ze strony kontaktowej
def wiadomosc_wyslij(request):
    response_message = "success"
    try:
        nowa_wiadomosc = Wiadomosc(email=request.POST['email'],
                                   nazwisko=request.POST['name'],
                                   tresc=request.POST['tresc'],
                                   odpowiedz='',
                                   wyslano_odpowiedz=False)
        nowa_wiadomosc.save()

    except ValueError:
        response_message = "site_error"

    except KeyError:
        raise Http404

    response = '{"message": "' + response_message + '" }'
    #response = '{"message": "success"}'
    return HttpResponse(response)


def wyslij_email(request, pk):
    if request.is_ajax():
        response_message = "success"

        wiadomosc = Wiadomosc.objects.get(id=pk)
        subject = 'Hotel Messiah'
        try:
            message = request.GET['message']
            message_html = '<h3>' + _('Twoje pytanie') + ': </h3><p>' + wiadomosc.tresc + \
                '</p><h3>' + _('Nasza odpowiedz') + ': </h3><p>' + request.GET['message'] + "</p>"
            from_email = 'hotel.messiah@gmail.com'
            to_email = request.GET['email_address']
            if subject and message and from_email:
                try:
                    # send_mail(subject, message, from_email, [to_email])
                    msg = EmailMessage(subject, message_html, from_email, [to_email])
                    msg.content_subtype = "html"
                    msg.send()
                except KeyError:
                    response_message = "site_error"
            else:
                response_message = "empty_field"

            if response_message == "success":
                wiadomosc.wyslano_odpowiedz = True
                wiadomosc.odpowiedz = message
                wiadomosc.save()
        except KeyError:
            raise Http404

        return HttpResponse(response_message)
    else:
        raise Http404


def wiadomosci_oznacz(request, pk):
    if request.is_ajax():
        try:
            w = Wiadomosc.objects.get(pk=pk)
            if w.wyslano_odpowiedz:
                w.wyslano_odpowiedz = False
                response = 'false'
            else:
                w.wyslano_odpowiedz = True
                response = 'true'
            w.save()
            return HttpResponse(response)
        except ObjectDoesNotExist:
            pass
    else:
        raise Http404


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
                                             cena=CenaPokoju.objects.get(rozmiar=Pokoj.objects.get(pk=list_of_pks[i]).rozmiar).cena)
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


# Widok wykonywany po kliknieciu 'Wyslij' w momencie edycji istniejacej rezerwacji
def rezerwacje_wyslij_kod(request, code):
    response_message = 'success'
    try:
        test_post = request.POST['name']
        requested_res = Rezerwacja.objects.get(kod=code)

        # Pewne rzeczy POST przekazuje w stringu wiec musimy je skonwertowac
        # Daty
        poczatek_pobytu_split = request.POST['date-from'].split('/')
        koniec_pobytu_split = request.POST['date-to'].split('/')
        poczatek_pobytu = date(int(poczatek_pobytu_split[2]), int(poczatek_pobytu_split[0]), int(poczatek_pobytu_split[1]))
        koniec_pobytu = date(int(koniec_pobytu_split[2]), int(koniec_pobytu_split[0]), int(koniec_pobytu_split[1]))

        # Nie mozemy mieszac w rezerwacji jesli sie juz zakonczyla
        if requested_res.koniec_pobytu >= datetime.date.today():

            # Ilosc pokojow
            ilosc_pokojow = int(request.POST['rooms'])

            # Ilosc doroslych i dzieci w pokojach
            dorosli = []
            dzieci = []
            ilosc_osob = []
            for i in range(1, ilosc_pokojow + 1):
                dorosli.append(int(request.POST['adults%d' % (i,)]))
                dzieci.append(int(request.POST['kids%d' % (i,)]))
                ilosc_osob.append(dorosli[i-1] + dzieci[i-1])

            # Jesli rezerwacja sie juz zaczela to nie mozemy zmienic poczatku rezerwacji
            if requested_res.poczatek_pobytu < datetime.date.today():
                poczatek_pobytu = requested_res.poczatek_pobytu

            # Wyszukujemy pokoje ktore na formularzu maja taka sama ilosc osob jak oryginalnie w rezerwacji
            # dla takich pokojow wystarczy sprawdzic czy sa wolne w nowych datach i jesli sa to nie trzeba
            # przeprowadzac klienta do nowego pokoju, moze zostac w tym ktory juz jest na rezerwacji

            # Wyszukujemy pokoje ktore maja wybrane tyle samo osob co na rezerwacji
            # Zapisujemy te pokoje oraz ich numery
            # numery zeby potem wiedziec ktorych z tablicy ilosc_osob nie musimy szukac (bo zostaly)
            pokoje_na_rezerwacji = PokojNaRezerwacji.objects.filter(rezerwacja=requested_res)
            pokoje_do_zachowania = []
            numery_do_zachowania = []
            for i in range(0, len(ilosc_osob)):
                for p in pokoje_na_rezerwacji:
                    if p.doroslych + p.dzieci == ilosc_osob[i] and not p in pokoje_do_zachowania:
                        pokoje_do_zachowania.append(p)
                        numery_do_zachowania.append(i+1)
                        break

            # Mamy pokoje, ktore maja tyle samo osob, ale teraz pozostaje kwestia, czy sa wolne w nowych datach
            # Jesli znajdziemy rezerwacje taka, ze pokoj potencjalnie do zachowania jest w nowej dacie zajety
            # to zapisujemy, zeby go usunac
            pokoje_do_zachowania_do_usuniecia = []
            for i in range(0, len(pokoje_do_zachowania)):
                for r in Rezerwacja.objects.filter(~Q(kod=code)):
                    if poczatek_pobytu <= r.poczatek_pobytu <= koniec_pobytu or \
                            koniec_pobytu >= r.koniec_pobytu >= poczatek_pobytu or \
                            r.poczatek_pobytu <= poczatek_pobytu <= r.koniec_pobytu:
                        if r.pokojnarezerwacji_set.filter(pokoj__pk=pokoje_do_zachowania[i].pokoj.pk):
                            pokoje_do_zachowania_do_usuniecia.append(pokoje_do_zachowania[i])
                            break

            # Usuwamy wsyzstkie pokoje i ich numery, ktore sa zajete w nowych datach (zostawiajac tylko te,
            # ktore maja taka sama ilosc osob ORAZ sa wolne w nowych datach)
            # zachowane_pokoje i zachowane_numery to finalne tablice przechowujace pokoje, ktorych nie usuwamy
            zachowane_pokoje = []
            zachowane_numery = []
            for i in range(0, len(pokoje_do_zachowania)):
                if not pokoje_do_zachowania[i] in pokoje_do_zachowania_do_usuniecia:
                    zachowane_pokoje.append(pokoje_do_zachowania[i])
                    zachowane_numery.append(numery_do_zachowania[i])

            # Liczymy ile nowych pokojow musimy znalezc
            ilosc_wymaganych_pokojow = 0
            for i in range(1, ilosc_pokojow + 1):
                if i not in zachowane_numery:
                    ilosc_wymaganych_pokojow += 1

            # Bedziemy wyszkiwac nowe pokoje tylko jesli w ogole sa jakies ktore musza
            # zostac zastopiane badz dodane
            list_of_pks = []
            wymagane_pokoje_numery = []
            if ilosc_wymaganych_pokojow > 0:

                for i in range(1, ilosc_pokojow + 1):
                    if i not in zachowane_numery:
                        wymagane_pokoje_numery.append(i)

                wymagane_pokoje = {'ilosc': ilosc_wymaganych_pokojow}
                for i in range(1, ilosc_wymaganych_pokojow + 1):
                    wymagane_pokoje['pokoj%d' % (i,)] = ilosc_osob[wymagane_pokoje_numery[i-1] - 1]

                wyszukane_pokoje = wyszukaj_pokoje(poczatek_pobytu, koniec_pobytu, wymagane_pokoje)

                for i in range(1, ilosc_wymaganych_pokojow + 1):
                    try:
                        list_of_pks.append(int(wyszukane_pokoje['pokoj%d' % (i,)]))
                    except ValueError:
                        response_message = 'rooms_error'
                        return HttpResponse(response_message)

            # Jestesmy w sytuacji, w ktorej jesli byly jakies pokoje dla ktorych trzeba bylo wyszukac nowe numery
            # zostalo to zrobione i mamy:
            # ilosc_wymaganych_pokojow : ilosc zmienionych pokojow
            # list_of_pks : tablica z nowymi pk pokojow
            # wymagane_pokoje_numery : numery pokojow (na stronie, 1-3, nie numer pokoju w hotelu), ktore zostaly zmienione
            #
            # Nastepujaca relacja:
            # n-ty pokoj do zmiany - jego nowy pk jest pod list_of_pks[n], jego numer na stonie jest pod wymagane_pokoje_numery[n]
            #
            # Jesli jakies pokoje pozostaly na rezerwacji mamy:
            # zachowane_pokoje : lista instancji klasy PokojNaRezerwacji, ktore zostaja
            # zachowane_numery : lista numerow na stronie pokojow ktore zostaja
            # z nastepujaca relacja
            # n-ty zachowany pokoj - odpowiadajaca mu instancja PokojNaRezerwacji jest pod zachowane_pokoje[n],
            # a jego numer na stronie jest pod zachowane_numery[n]

            for pnr in pokoje_na_rezerwacji:
                if pnr not in zachowane_pokoje:
                    pnr.delete()

            for i in range(0, ilosc_wymaganych_pokojow):
                nowy_pnr = PokojNaRezerwacji(rezerwacja=requested_res,
                                             pokoj=Pokoj.objects.get(pk=list_of_pks[i]),
                                             doroslych=dorosli[wymagane_pokoje_numery[i]-1],
                                             dzieci=dzieci[wymagane_pokoje_numery[i]-1],
                                             cena=CenaPokoju.objects.get(rozmiar=Pokoj.objects.get(pk=list_of_pks[i]).rozmiar).cena)
                nowy_pnr.save()

            # USLUGI

            # Tworzymy liste pk zamowionych uslug
            uslugi = []
            for k, v in request.POST.items():
                if k.startswith('in') or k.startswith('out'):
                    uslugi.append(int(v))

            for unr in UslugaNaRezerwacji.objects.filter(rezerwacja=requested_res):
                if not unr.usluga.pk in uslugi:
                    unr.delete()

            uslugi_na_rezerwacji = []
            for unr in UslugaNaRezerwacji.objects.filter(rezerwacja=requested_res):
                uslugi_na_rezerwacji.append(unr.usluga.pk)

            for u in uslugi:
                if u not in uslugi_na_rezerwacji:
                    nowa_unr = UslugaNaRezerwacji(rezerwacja=requested_res,
                                                  usluga=Usluga.objects.get(pk=u),
                                                  cena=0)
                    nowa_unr.save()

            # DATY I DODATKOWE ZYCZENIA

            requested_res.poczatek_pobytu = poczatek_pobytu
            requested_res.koniec_pobytu = koniec_pobytu
            requested_res.dodatkowe_instrukcje = request.POST['requests']
            requested_res.save()

        return HttpResponse(response_message)

    # Nie zostal przekazany POST
    except KeyError:
        raise Http404


def rezerwacje_anuluj(request, code):
    if request.is_ajax():
        try:
            r = Rezerwacja.objects.get(kod=code)
            if r.poczatek_pobytu <= datetime.date.today():
                return HttpResponse('date')
            r.delete()
            return HttpResponse('success')
        except ObjectDoesNotExist:
            return HttpResponse('fail')
    else:
        raise Http404


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

            list_of_pks = wyszukaj_pokoje(poczatek_pobytu, koniec_pobytu, wymagane_pokoje, request.GET['kod'])

            # Tworzymy JSON zawierajacy statusy wszyskich pokojow
            response = '{'
            for i in range(1, wymagane_pokoje['ilosc'] + 1):
                response += '"pokoj%d": "%s", ' % (i, str(list_of_pks['pokoj%d' % (i,)]))

            # Dodajemy do JSONa koszt wynajecia pokoju na tyle dni
            cena_dorosly = OpisHotelu.objects.filter()[0].cena_dorosly
            cena_dziecko = OpisHotelu.objects.filter()[0].cena_dziecko
            ile_dni = (koniec_pobytu - poczatek_pobytu).days
            cena = 0
            for i in range(1, wymagane_pokoje['ilosc'] + 1):
                try:
                    p = Pokoj.objects.get(pk=int(list_of_pks['pokoj%d' % (i,)]))
                    cena += CenaPokoju.objects.get(rozmiar=p.rozmiar).cena * ile_dni
                    cena += cena_dorosly * ile_dni * dorosli_dzieci['dorosli%d' % (i,)]
                    cena += cena_dziecko * ile_dni * dorosli_dzieci['dzieci%d' % (i,)]
                except ValueError:
                    pass
                except ObjectDoesNotExist:
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
        res = Rezerwacja.objects.filter(zarchiwizowany=False, koniec_pobytu__gt=datetime.date.today())
        if res.filter(kod=code):
            response = 'true'
        else:
            response = 'false'
        return HttpResponse(response)
    else:
        raise Http404


def rezerwacje_sprawdz_email(request, email):
    if request.is_ajax():
        res = Rezerwacja.objects.filter(zarchiwizowany=False, koniec_pobytu__gt=datetime.date.today())
        res = res.filter(email=email)
        if res:
            return render(request, 'hotel/rezerwacje_przypkodow.html', {'rezerwacje': res})
        else:
            return HttpResponse('')
    else:
        raise Http404


def rezerwacje_kod(request, code):
    try:
        requested_res = Rezerwacja.objects.filter(zarchiwizowany=False, koniec_pobytu__gt=datetime.date.today())
        requested_res = requested_res.get(kod=code)

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

        context = {
            'uslugi_all': Usluga.objects.all(),
            'uslugi_wewnetrzne': uslugi_wewnetrzne,
            'uslugi_zewnetrzne': uslugi_zewnetrzne,
            'rezerwacja_do_edycji': requested_res,
            'poczatek_pobytu': poczatek_pobytu,
            'koniec_pobytu': koniec_pobytu,
            'liczba_pokoi': liczba_pokoi,
            'uslugi': uslugi
        }

        # Ilosc osob w poszczegolnych pokojach
        i = 1
        for pnr in PokojNaRezerwacji.objects.filter(rezerwacja=requested_res):
            context['doroslych%d' % (i,)] = pnr.doroslych
            context['dzieci%d' % (i,)] = pnr.dzieci
            i += 1

        return render(request, 'hotel/rezerwacje.html', include_header_footer(context))

    except ObjectDoesNotExist:
        raise Http404


def rezerwacje_istnieje(request):
    return render(request, 'hotel/rezerwacje_ist.html', include_header_footer())
