from django.db import models

# Rzeczy do dodania do modelu:
# - rezerwacja - cos jak boolean czy jest aktywna czy nie
# - wiadomosci - data


class Usluga(models.Model):
    nazwa = models.CharField(max_length=60)
    cena = models.CharField(max_length=100)
    opis = models.TextField(blank=True)
    dostepnosc = models.BooleanField()
    zewnetrzna = models.BooleanField()

    def __unicode__(self):
        return self.nazwa


class Pokoj(models.Model):
    numer = models.IntegerField()
    rozmiar = models.IntegerField()        # Ilosc osob.
    opis = models.TextField(blank=True)
    opis_combo = models.CharField(max_length=30)
    dostepnosc = models.BooleanField(default=True, verbose_name='Jest dostepny')
    cena = models.DecimalField(max_digits=6, decimal_places=2)

    def __unicode__(self):
        return '%d, rozmiar - %d' % (self.numer, self.rozmiar,)


class ZdjeciaPokojow(models.Model):
    zdjecie = models.ImageField(upload_to='pokoje')
    pokoj = models.ForeignKey(Pokoj)


class Rezerwacja(models.Model):
    poczatek_pobytu = models.DateField('Poczatek pobytu')
    koniec_pobytu = models.DateField('Koniec pobytu')
    email = models.EmailField(max_length=254)
    telefon = models.CharField(max_length=40, blank=True)
    nazwisko = models.CharField(max_length=50)
    dodatkowe_instrukcje = models.TextField(blank=True)
    kod = models.CharField(max_length=12)
    notatka = models.TextField(blank=True)

    cena_dorosly = models.DecimalField(max_digits=6, decimal_places=2)
    cena_dziecko = models.DecimalField(max_digits=6, decimal_places=2)
    uslugi = models.ManyToManyField(Usluga, through='UslugaNaRezerwacji')
    pokoje = models.ManyToManyField(Pokoj, through='PokojNaRezerwacji')

    def __unicode__(self):
        return self.email


# Model reprezentujacy tabelke pomiedzy Rezerwacja a Pokojem
# w many-to-many relationship
class PokojNaRezerwacji(models.Model):
    rezerwacja = models.ForeignKey(Rezerwacja)
    pokoj = models.ForeignKey(Pokoj)
    doroslych = models.IntegerField(blank=True)
    dzieci = models.IntegerField(blank=True)
    cena = models.DecimalField(max_digits=6, decimal_places=2)


# Model reprezentujacy tabelke pomiedzy Rezerwacja a Usluga
# w many-to-many relationship
class UslugaNaRezerwacji(models.Model):
    rezerwacja = models.ForeignKey(Rezerwacja)
    usluga = models.ForeignKey(Usluga)
    cena = models.DecimalField(max_digits=6, decimal_places=2, blank=True)


class KategoriaJedzenia(models.Model):
    nazwa = models.CharField(max_length=30)
    opis = models.TextField(blank=True)

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
    url_mapy = models.URLField(max_length=1000, blank=True)

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


class ZdjeciaHotelu(models.Model):
    zdjecie = models.ImageField(upload_to='hotel/galeria')


class Wiadomosc(models.Model):
    email = models.EmailField(max_length=254)
    nazwisko = models.CharField(max_length=50)
    tresc = models.TextField()
    odpowiedz = models.TextField(blank=True)
    wyslano_odpowiedz = models.BooleanField()