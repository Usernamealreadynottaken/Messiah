from django.db import models


class Usluga(models.Model):
    nazwa = models.CharField(max_length=60)
    cena = models.DecimalField(max_digits=6, decimal_places=2)
    opis = models.TextField(null=True)
    dostepnosc = models.BooleanField()
    zewnetrzna = models.BooleanField()


class Pokoj(models.Model):
    numer = models.IntegerField()
    rozmiar = models.IntegerField()        # Ilosc osob.
    ilosc_lozek = models.IntegerField(null=True)
    opis = models.TextField(null=True)
    opis_combo = models.CharField(max_length=30)
    dostepnosc = models.NullBooleanField()
    cena = models.DecimalField(max_digits=6, decimal_places=2)


class ZdjeciaPokojow(models.Model):
    zdjecie = models.ImageField(upload_to='pokoje')
    pokoj = models.ForeignKey(Pokoj)


class Rezerwacja(models.Model):
    poczatek_pobytu = models.DateField('Poczatek pobytu')
    koniec_pobytu = models.DateField('Koniec pobytu')
    doroslych = models.IntegerField(null=True)
    dzieci = models.IntegerField(null=True)
    email = models.EmailField(max_length=254)
    telefon = models.CharField(max_length=40, null=True)
    nazwisko = models.CharField(max_length=50)
    dodatkowe_instrukcje = models.TextField()
    kod = models.CharField(max_length=12)

    uslugi = models.ManyToManyField(Usluga, through='UslugaNaRezerwacji')
    pokoje = models.ManyToManyField(Pokoj, through='PokojNaRezerwacji')


class PokojNaRezerwacji(models.Model):
    rezerwacja = models.ForeignKey(Rezerwacja)
    pokoj = models.ForeignKey(Pokoj)
    cena = models.DecimalField(max_digits=6, decimal_places=2)


# Model reprezentujacy tabelke pomiedzy Rezerwacja a Usluga
# w many-to-many relationship
class UslugaNaRezerwacji(models.Model):
    rezerwacja = models.ForeignKey(Rezerwacja)
    usluga = models.ForeignKey(Usluga)
    cena = models.DecimalField(max_digits=6, decimal_places=2)


class KategoriaJedzenia(models.Model):
    nazwa = models.CharField(max_length=30)


class Jedzenie(models.Model):
    nazwa = models.CharField(max_length=100)
    cena = models.DecimalField(max_digits=6, decimal_places=2)
    opis = models.TextField(null=True)
    zdjecie = models.ImageField(upload_to='jedzenie', null=True)

    kategoria = models.ForeignKey(KategoriaJedzenia)


class OpisHotelu(models.Model):
    # Dane techniczne
    cena_dorosly = models.DecimalField(max_digits=6, decimal_places=2)
    cena_dziecko = models.DecimalField(max_digits=6, decimal_places=2)

    # Opis na stronie glownej
    opis_hotelu = models.TextField()
    # meta description
    opis_google = models.CharField(max_length=200)

    # Stopka
    skype = models.CharField(max_length=30, null=True)
    gadu_gadu = models.CharField(max_length=15, null=True)
    email = models.EmailField(max_length=254, null=True)
    facebook = models.URLField(null=True)         # Default max_length = 200
    twitter = models.CharField(max_length=40, null=True)

    # Google Maps
    wyswietlaj_mape = models.BooleanField()
    url_mapy = models.URLField(max_length=1000, null=True)

    # Logo
    logo = models.ImageField(upload_to='hotel')
    tekst_logo = models.CharField(max_length=30, null=True)
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