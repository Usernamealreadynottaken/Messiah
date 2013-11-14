from django.db import models
from django import forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Q

# Rzeczy do dodania do modelu:
# - rezerwacja - cos jak boolean czy jest aktywna czy nie
# - wiadomosci - data


class Usluga(models.Model):
    nazwa = models.CharField(max_length=60)
    cena = models.CharField(max_length=100)
    opis = models.TextField(blank=True)
    dostepnosc = models.BooleanField()
    zewnetrzna = models.BooleanField()

    class Meta:
        verbose_name = 'Usluga'
        verbose_name_plural = 'Uslugi'
        ordering = ['-dostepnosc', 'zewnetrzna', 'nazwa']

    def __unicode__(self):
        return self.nazwa

    def wewnetrzna(self):
        return not self.zewnetrzna

    dostepnosc.boolean = True
    dostepnosc.verbose_name = 'Jest dostepna?'
    wewnetrzna.boolean = True


class Pokoj(models.Model):
    numer = models.IntegerField()
    rozmiar = models.IntegerField()        # Ilosc osob.
    opis = models.TextField(blank=True)
    opis_combo = models.CharField(max_length=30)
    dostepnosc = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Pokoj'
        verbose_name_plural = 'Pokoje'
        ordering = ['-dostepnosc', 'numer']

    def __unicode__(self):
        ret = 'Numer: %d, rozmiar: %d' % (self.numer, self.rozmiar,)
        if not self.dostepnosc:
            ret += ' (Niedostepny!)'
        return ret

    dostepnosc.boolean = True
    dostepnosc.verbose_name = 'Jest dostepny?'


class CenaPokoju(models.Model):
    rozmiar = models.IntegerField(unique=True)
    cena = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = 'Cena pokoju'
        verbose_name_plural = 'Ceny pokojow'
        ordering = ['rozmiar']

    def __unicode__(self):
        return 'Rozmiar: %d, cena: %d' % (self.rozmiar, self.cena,)


class ZdjeciaPokojow(models.Model):
    zdjecie = models.ImageField(upload_to='pokoje')
    pokoj = models.ForeignKey(Pokoj)

    class Meta:
        verbose_name = 'Zdjecie pokoju'
        verbose_name_plural = 'Zdjecia pokojow'


class Rezerwacja(models.Model):
    poczatek_pobytu = models.DateField('Poczatek pobytu')
    koniec_pobytu = models.DateField('Koniec pobytu')
    email = models.EmailField(max_length=254)
    telefon = models.CharField(max_length=40, blank=True)
    nazwisko = models.CharField(max_length=50)
    dodatkowe_instrukcje = models.TextField(blank=True)
    kod = models.CharField(max_length=12)
    notatka = models.TextField(blank=True)
    zarchiwizowany = models.BooleanField(default=False, blank=True)

    cena_dorosly = models.DecimalField(max_digits=6, decimal_places=2)
    cena_dziecko = models.DecimalField(max_digits=6, decimal_places=2)
    uslugi = models.ManyToManyField(Usluga, through='UslugaNaRezerwacji')
    pokoje = models.ManyToManyField(Pokoj, through='PokojNaRezerwacji')

    class Meta:
        verbose_name = 'Rezerwacja'
        verbose_name_plural = 'Rezerwacje'
        ordering = ['-poczatek_pobytu']

    def __unicode__(self):
        return self.email

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
                pv += ' i '
            pv += '%d (%d osob' % (pnr.pokoj.numer, pnr.osob(),)
            if pnr.osob() == 1:
                pv += 'a'
            elif pnr.osob() <= 4:
                pv += 'y'
            pv += ')'
            i += 1

        return pv

    pokoje_verbose.short_description = 'Pokoje na rezerwacji'


class RezerwacjaForm(forms.ModelForm):
    my_field = forms.CharField()

    class Meta:
        model = Rezerwacja

    def __init__(self, *args, **kwargs):
        super(RezerwacjaForm, self).__init__(*args, **kwargs)
        self.fields['my_field'] = forms.CharField(label='ELOOOO', initial='Some some')


# Model reprezentujacy tabelke pomiedzy Rezerwacja a Pokojem
# w many-to-many relationship
class PokojNaRezerwacji(models.Model):
    rezerwacja = models.ForeignKey(Rezerwacja)
    pokoj = models.ForeignKey(Pokoj)

    doroslych = models.IntegerField(blank=True, null=True)
    dzieci = models.IntegerField(blank=True, null=True)
    cena = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = 'Pokoj na rezerwacji'
        verbose_name_plural = 'Pokoje na rezerwacji'

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
                    raise ValidationError('Pokoj zostal dodany wiecej niz raz.')

            # Czy pokoj jest wolny w danym terminie
            poczatek_pobytu = self.rezerwacja.poczatek_pobytu
            koniec_pobytu = self.rezerwacja.koniec_pobytu

            for r in Rezerwacja.objects.filter(~Q(pk=self.rezerwacja.pk)):
                if poczatek_pobytu <= r.poczatek_pobytu < koniec_pobytu or \
                        koniec_pobytu >= r.koniec_pobytu > poczatek_pobytu or \
                        r.poczatek_pobytu <= poczatek_pobytu < r.koniec_pobytu:
                    if r.pokojnarezerwacji_set.filter(pokoj__pk=self.pokoj.pk):
                        raise ValidationError('Ten pokoj jest zajety w tym terminie.')
        except ObjectDoesNotExist:
            pass


# Model reprezentujacy tabelke pomiedzy Rezerwacja a Usluga
# w many-to-many relationship
class UslugaNaRezerwacji(models.Model):
    rezerwacja = models.ForeignKey(Rezerwacja)
    usluga = models.ForeignKey(Usluga)
    cena = models.DecimalField(max_digits=6, decimal_places=2, blank=True)

    class Meta:
        verbose_name = 'Usluga na rezerwacji'
        verbose_name_plural = 'Uslugi na rezerwacji'


class KategoriaJedzenia(models.Model):
    nazwa = models.CharField(max_length=30)
    opis = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Kategoria jedzenia'
        verbose_name_plural = 'Kategorie jedzenia'

    def __unicode__(self):
        return self.nazwa


class Jedzenie(models.Model):
    nazwa = models.CharField(max_length=100)
    cena = models.DecimalField(max_digits=6, decimal_places=2)
    opis = models.TextField(blank=True)
    zdjecie = models.ImageField(upload_to='jedzenie', blank=True)

    kategoria = models.ForeignKey(KategoriaJedzenia)

    def __unicode__(self):
        return self.nazwa


class OpisHotelu(models.Model):
    # Dane techniczne
    cena_dorosly = models.DecimalField(max_digits=6, decimal_places=2)
    cena_dziecko = models.DecimalField(max_digits=6, decimal_places=2)

    # Opis na stronie glownej
    opis_hotelu = models.TextField()
    zdjecie = models.ImageField(upload_to='hotel')
    # meta description
    opis_google = models.CharField(max_length=200)

    # Stopka
    skype = models.CharField(max_length=30, blank=True)
    gadu_gadu = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    facebook = models.URLField(blank=True)         # Default max_length = 200
    twitter = models.CharField(max_length=40, blank=True)

    # Google Maps
    wyswietlaj_mape = models.BooleanField()
    html_mapy_google = models.TextField(blank=True)

    # Logo
    logo = models.ImageField(upload_to='hotel/logo')
    tekst_logo = models.CharField(max_length=30, blank=True)
    tekst_logo_widoczny = models.BooleanField()
    # Wartosc pola sklada sie z dwoch liter:
    # pierwsza to rozmiar logo: 'D' - duze, 'M' - male
    # druga to polozenie tekstu w stosunku do logo: 'G' - gore, 'D' - dol, 'P' - prawo, 'L' - lewo
    UKLAD_CHOICES = (
        ('DD', 'Duze logo, tekst pod spodem'),
        ('DG', 'Duze logo, tekst na gorze'),
        ('ML', 'Male logo, tekst z lewej strony'),
        ('MP', 'Male logo, tekst z prawej strony'),
    )
    uklad = models.CharField(max_length=2, choices=UKLAD_CHOICES, default='DD')

    class Meta:
        verbose_name = 'Ustawienia i dane hotelu'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return 'Ustawienia i dane hotelu'


class ZdjeciaHotelu(models.Model):
    zdjecie = models.ImageField(upload_to='hotel/galeria')

    class Meta:
        verbose_name = 'Zdjecie hotelu'
        verbose_name_plural = 'Zdjecia hotelu'


class Wiadomosc(models.Model):
    email = models.EmailField(max_length=254)
    nazwisko = models.CharField(max_length=50)
    tresc = models.TextField()
    odpowiedz = models.TextField(blank=True)
    wyslano_odpowiedz = models.BooleanField()

    class Meta:
        verbose_name = 'Wiadomosc'
        verbose_name_plural = 'Wiadomosci'