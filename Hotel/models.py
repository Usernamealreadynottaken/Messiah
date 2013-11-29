from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _, ungettext_lazy as __, ugettext as _u, ungettext

# Rzeczy do dodania do modelu:
# - rezerwacja - cos jak boolean czy jest aktywna czy nie
# - wiadomosci - data


class Usluga(models.Model):
    nazwa = models.CharField(_('Nazwa'), max_length=60)
    cena = models.CharField(_('Cena'), max_length=100)
    opis = models.TextField(_('Opis'), blank=True)
    dostepnosc = models.BooleanField(_('Dostepnosc'))
    zewnetrzna = models.BooleanField(_('Zewnetrzna'))

    class Meta:
        verbose_name = _('Usluga')
        verbose_name_plural = _('Uslugi')
        ordering = ['-dostepnosc', 'zewnetrzna', 'nazwa']

    def __unicode__(self):
        return self.nazwa

    def wewnetrzna(self):
        return not self.zewnetrzna

    dostepnosc.boolean = True
    dostepnosc.verbose_name = _('Jest dostepna?')
    wewnetrzna.boolean = True
    wewnetrzna.verbose_name = _('Wewnetrzna')


class Pokoj(models.Model):
    numer = models.IntegerField(_('Numer'))
    rozmiar = models.IntegerField(_('Rozmiar'))        # Ilosc osob.
    opis = models.TextField(_('Opis'), blank=True)
    opis_combo = models.CharField(_('Krotki opis'), max_length=30)
    dostepnosc = models.BooleanField(_('Dostepnosc'), default=True)

    class Meta:
        verbose_name = _('Pokoj')
        verbose_name_plural = _('Pokoje')
        ordering = ['-dostepnosc', 'numer']

    def __unicode__(self):
        ret = _('Numer: %(numer)d, rozmiar: %(rozmiar)d') % {'numer': self.numer, 'rozmiar': self.rozmiar, }
        if not self.dostepnosc:
            ret += ' (' + _u('Niedostepny!') + ')'
        return ret

    dostepnosc.boolean = True
    dostepnosc.verbose_name = _('Jest dostepny?')


class CenaPokoju(models.Model):
    rozmiar = models.IntegerField(_('Rozmiar'), unique=True)
    cena = models.DecimalField(_('Cena'), max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = _('Cena pokoju')
        verbose_name_plural = _('Ceny pokojow')
        ordering = ['rozmiar']

    def __unicode__(self):
        return _('Rozmiar: %(rozmiar)d, cena: %(cena)d') % {'rozmiar': self.rozmiar, 'cena': self.cena, }


class ZdjeciaPokojow(models.Model):
    zdjecie = models.ImageField(_('Zdjecie'), upload_to='pokoje')
    pokoj = models.ForeignKey(Pokoj)

    class Meta:
        verbose_name = _('Zdjecie pokoju')
        verbose_name_plural = _('Zdjecia pokojow')


class Rezerwacja(models.Model):
    poczatek_pobytu = models.DateField(_('Poczatek pobytu'))
    koniec_pobytu = models.DateField(_('Koniec pobytu'))
    email = models.EmailField(_('E-mail'), max_length=254)
    telefon = models.CharField(_('Telefon'), max_length=40, blank=True)
    nazwisko = models.CharField(_('Nazwisko'), max_length=50)
    dodatkowe_instrukcje = models.TextField(_('Dodatkowe instrukcje'), blank=True)
    kod = models.CharField(_('Kod'), max_length=12)
    notatka = models.TextField(_('Notatka'), blank=True)
    zarchiwizowany = models.BooleanField(_('Zarchiwizowany'), default=False, blank=True)

    cena_dorosly = models.DecimalField(_('Cena dorosly'), max_digits=6, decimal_places=2)
    cena_dziecko = models.DecimalField(_('Cena dziecko'), max_digits=6, decimal_places=2)
    uslugi = models.ManyToManyField(Usluga, through='UslugaNaRezerwacji')
    pokoje = models.ManyToManyField(Pokoj, through='PokojNaRezerwacji')

    class Meta:
        verbose_name = _('Rezerwacja')
        verbose_name_plural = _('Rezerwacje')
        ordering = ['-poczatek_pobytu']

    def __unicode__(self):
        return self.nazwisko

    def wartosc_rezerwacji(self):
        dni = (self.koniec_pobytu - self.poczatek_pobytu).days
        cena = 0
        for pokoj in self.pokojnarezerwacji_set.all():
            cena += dni * (pokoj.cena + self.cena_dorosly * pokoj.doroslych + self.cena_dziecko * pokoj.dzieci)
        for usluga in self.usluganarezerwacji_set.all():
            cena += usluga.cena
        return cena

    def pokoje_verbose(self):
        pv = ''
        i = 0
        for pnr in self.pokojnarezerwacji_set.all():
            if 0 < i < self.pokojnarezerwacji_set.count() - 1:
                pv += ', '
            elif i == self.pokojnarezerwacji_set.count() - 1 and not i == 0:
                pv += ' ' + _u('i') + ' '

            pv += '%d (' % (pnr.pokoj.numer,)
            pv += ungettext('%d osoba', '%d osoby', pnr.osob()) % (pnr.osob(),)
            pv += ')'
            i += 1

        return pv

    pokoje_verbose.short_description = _('Pokoje na rezerwacji')


# Model reprezentujacy tabelke pomiedzy Rezerwacja a Pokojem
# w many-to-many relationship
class PokojNaRezerwacji(models.Model):
    rezerwacja = models.ForeignKey(Rezerwacja)
    pokoj = models.ForeignKey(Pokoj)

    doroslych = models.IntegerField(_('Doroslych'), blank=True, null=True)
    dzieci = models.IntegerField(_('Dzieci'), blank=True, null=True)
    cena = models.DecimalField(_('Cena'), max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = _('Pokoj na rezerwacji')
        verbose_name_plural = _('Pokoje na rezerwacji')

    def __unicode__(self):
        pnr = PokojNaRezerwacji.objects.filter(rezerwacja=self.rezerwacja)

        # Na wszelki wypadek jesli z jakiegos powodu jest 0
        if pnr:
            for i in range(0, len(pnr)):
                if pnr[i] == self:
                    return _u('Pokoj %d') % (i+1,)
        return _u('Pokoj na rezerwacji')

    def osob(self):
        return self.doroslych + self.dzieci

    def clean(self):
        # Jezeli ktoras z cen dla doroslych albo dzieci nie jest ustawiona to recznie
        # wpisujemy tam 0. Rozwiazanie jest takie zamiast ustawic null=True, bo wtedy jesli
        # uzytkownik nie wpisze nic do bazy zostanie wpisany NULL i nie wiem czy reszta
        # pythona bedzie traktowac NULL jako 0
        if not self.doroslych:
            self.doroslych = 0
        if not self.dzieci:
            self.dzieci = 0

        super(PokojNaRezerwacji, self).clean()

        # Wszystko w try, bo jesli np. uzytkownik wybierze jakis pokoj, wystapi blad (wiec sie nie zapisze)
        # i uzytkownik zrezygnuje i zmieni na '----' (pusty) to wysypuje sie ObjectDoesNotExist
        try:

            # Czy pokoj nie zostal dodany wiecej niz raz
            for pnr in self.rezerwacja.pokojnarezerwacji_set.filter(~Q(pk=self.pk)):
                print pnr.pokoj.numer
                if pnr.pokoj.pk == self.pokoj.pk:
                    raise ValidationError(_('Pokoj zostal dodany wiecej niz raz.'))

            # Czy pokoj jest wolny w danym terminie
            poczatek_pobytu = self.rezerwacja.poczatek_pobytu
            koniec_pobytu = self.rezerwacja.koniec_pobytu

            for r in Rezerwacja.objects.filter(~Q(pk=self.rezerwacja.pk)):
                if poczatek_pobytu <= r.poczatek_pobytu < koniec_pobytu or \
                        koniec_pobytu >= r.koniec_pobytu > poczatek_pobytu or \
                        r.poczatek_pobytu <= poczatek_pobytu < r.koniec_pobytu:
                    if r.pokojnarezerwacji_set.filter(pokoj__pk=self.pokoj.pk):
                        raise ValidationError(_('Ten pokoj jest zajety w tym terminie.'))
        except ObjectDoesNotExist:
            pass


# Model reprezentujacy tabelke pomiedzy Rezerwacja a Usluga
# w many-to-many relationship
class UslugaNaRezerwacji(models.Model):
    rezerwacja = models.ForeignKey(Rezerwacja)
    usluga = models.ForeignKey(Usluga)
    cena = models.DecimalField(_('Cena'), max_digits=6, decimal_places=2, blank=True)

    class Meta:
        verbose_name = _('Usluga na rezerwacji')
        verbose_name_plural = _('Uslugi na rezerwacji')

    def __unicode__(self):
        unr = UslugaNaRezerwacji.objects.filter(rezerwacja=self.rezerwacja)
        if unr:
            for i in range(0, len(unr)):
                if unr[i] == self:
                    return _u('Usluga %d') % (i+1,)
        return _u('Usluga na rezerwacji')

    def clean(self):
        # Jesli uzytkownik zostawi pusta cene to ustawiamy na 0 zeby nie wyskoczylo ze cena
        # nie moze byc nullem. Rozwiazanie takie samiast zostawc blank=False lub ustawic Null=True
        # poniewaz:
        # a) zmuszanie uzytkownika do podawania 0 jest uciazliwe jesli mozna to zautomatyzowac
        # b) jesli ustawimy Null=True to bez podania ceny w bazie danych zostaje ustawiony NULL i nie wiem
        #    czy reszta pythona bedzie traktowac taki NULL jak 0
        if not self.cena:
            self.cena = 0

        super(UslugaNaRezerwacji, self).clean()


class KategoriaJedzenia(models.Model):
    nazwa = models.CharField(_('Nazwa'), max_length=30)
    opis = models.TextField(_('Cena'), blank=True)

    class Meta:
        verbose_name = _('Kategoria jedzenia')
        verbose_name_plural = _('Kategorie jedzenia')

    def __unicode__(self):
        return self.nazwa


class Jedzenie(models.Model):
    nazwa = models.CharField(_('Nazwa'), max_length=100)
    cena = models.DecimalField(_('Cena'), max_digits=6, decimal_places=2)
    opis = models.TextField(_('Opis'), blank=True)
    zdjecie = models.ImageField(_('Zdjecie'), upload_to='jedzenie', blank=True)

    kategoria = models.ForeignKey(KategoriaJedzenia)

    class Meta:
        verbose_name = _('Jedzenie')
        verbose_name_plural = _('Jedzenie_PL')

    def __unicode__(self):
        return self.nazwa


class OpisHotelu(models.Model):
    # Dane techniczne
    cena_dorosly = models.DecimalField(_('Cena dorosly'), max_digits=6, decimal_places=2)
    cena_dziecko = models.DecimalField(_('Cena dzieck'), max_digits=6, decimal_places=2)

    # Opis na stronie glownej
    opis_hotelu = models.TextField(_('Opis hotelu'))
    zdjecie = models.ImageField(_('Zdjecie'), upload_to='hotel')
    # meta description
    opis_google = models.CharField(_('Opis google'), max_length=200)

    # Dane dla strony kontaktowej
    adres = models.CharField(_('Adres'), max_length=500, blank=True)
    telefon = models.CharField(_('Telefon'), max_length=40, blank=True)

    # Stopka
    skype = models.CharField(max_length=30, blank=True)
    gadu_gadu = models.CharField(max_length=15, blank=True)
    email = models.EmailField(_('E-mail'), max_length=254, blank=True)
    facebook = models.URLField(blank=True)         # Default max_length = 200
    twitter = models.CharField(max_length=40, blank=True)

    # Google Maps
    wyswietlaj_mape = models.BooleanField(_('Wyswietlaj mape'))
    html_mapy_google = models.TextField(_('HTML mapy Google'), blank=True)

    # Logo
    logo = models.ImageField(_('Logo'), upload_to='hotel/logo')
    tekst_logo = models.CharField(_('Tekst obok logo'), max_length=30, blank=True)
    tekst_logo_widoczny = models.BooleanField(_('Teks obok logo widoczny'))
    # Wartosc pola sklada sie z dwoch liter:
    # pierwsza to rozmiar logo: 'D' - duze, 'M' - male
    # druga to polozenie tekstu w stosunku do logo: 'G' - gore, 'D' - dol, 'P' - prawo, 'L' - lewo
    UKLAD_CHOICES = (
        ('DD', _('Duze logo, tekst pod spodem')),
        ('DG', _('Duze logo, tekst na gorze')),
        ('ML', _('Male logo, tekst z lewej strony')),
        ('MP', _('Male logo, tekst z prawej strony')),
    )
    uklad = models.CharField(_('Uklad'), max_length=2, choices=UKLAD_CHOICES, default='DD')

    class Meta:
        verbose_name = _('Ustawienia')
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return _('Ustawienia')


class ZdjeciaHotelu(models.Model):
    zdjecie = models.ImageField(_('Zdjecie'), upload_to='hotel/galeria')

    class Meta:
        verbose_name = _('Zdjecie hotelu')
        verbose_name_plural = _('Zdjecia hotelu')


class Wiadomosc(models.Model):
    email = models.EmailField(_('E-mail'), max_length=254)
    nazwisko = models.CharField(_('Nazwisko'), max_length=50)
    tresc = models.TextField(_('Tresc'))
    odpowiedz = models.TextField(_('Odpowiedz'), blank=True)
    wyslano_odpowiedz = models.BooleanField(_('Wyslano odpowiedz'))
    data = models.DateTimeField(_('Data'), auto_now=True, null=True)

    class Meta:
        verbose_name = _('Wiadomosc')
        verbose_name_plural = _('Wiadomosci')


class Newsletter(models.Model):
    news_email = models.EmailField(_('E-mail'), max_length=254)

    class Meta:
        verbose_name = _('Biuletyn - lista')
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.news_email