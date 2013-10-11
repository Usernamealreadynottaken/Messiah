from django.db import models

# TODO:
# - przejrzec upload_to dla wszystkich obrazkow i uzgodnic strukture folderow z mediami
# - ustalic ktore wartosci moga byc NULL


class Rezerwacja(models.Model):
    poczatek_pobytu = models.DateTimeField('Poczatek pobytu')
    koniec_pobytu = models.DateTimeField('Koniec pobytu')
    doroslych = models.IntegerField()
    dzieci = models.IntegerField()
    email = models.EmailField(max_length=254)
    telefon = models.CharField(max_length=40)
    nazwisko = models.CharField(max_length=50)
    dodatkowe_instrukcje = models.TextField()
    kod = models.CharField(max_length=12)
    uslugi = models.TextField()

    # Pokoj
    numer_pokoju = models.IntegerField()
    opis_pokoju = models.TextField()


class Usluga(models.Model):
    nazwa = models.CharField(max_length=60)
    cena = models.FloatField()
    opis = models.TextField()
    dostepnosc = models.BooleanField()
    zewnetrzna = models.BooleanField()


class Pokoj(models.Model):
    numer = models.IntegerField()
    rozmiar = models.IntegerField()        # Ilosc osob.
    ilosc_lozek = models.IntegerField()
    opis = models.TextField()
    dostepnosc = models.NullBooleanField()
    cena = models.FloatField()


class ZdjeciaPokojow(models.Model):
    zdjecie = models.ImageField(upload_to='pokoje')
    pokoj = models.ForeignKey(Pokoj)


class KategoriaJedzenia(models.Model):
    nazwa = models.CharField(max_length=30)


class Jedzenie(models.Model):
    nazwa = models.CharField(max_length=100)
    cena = models.FloatField()
    opis = models.TextField()
    zdjecie = models.ImageField(upload_to='jedzenie')

    kategoria = models.ForeignKey(KategoriaJedzenia)


class OpisHotelu(models.Model):
    opis_hotelu = models.TextField()

    # Stopka
    skype = models.CharField(max_length=30)
    gadu_gadu = models.CharField(max_length=15)
    email = models.EmailField(max_length=254)
    facebook = models.URLField()         # Default max_length = 200
    twitter = models.CharField(max_length=40)

    # Google Maps
    wyswietlaj_mape = models.BooleanField()
    url_mapy = models.URLField(max_length=1000)

    # Logo
    logo = models.ImageField(upload_to='hotel')
    tekst_logo = models.CharField(max_length=30)
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