from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline
from django.utils.translation import ugettext as _
import datetime

from Hotel.models import Rezerwacja, Pokoj, Usluga, UslugaNaRezerwacji, PokojNaRezerwacji, Wiadomosc, KategoriaJedzenia, Jedzenie, \
    ZdjeciaPokojow, CenaPokoju, OpisHotelu, ZdjeciaHotelu, Newsletter


# REZERWACJE

class UslugaInline(admin.TabularInline):
    model = UslugaNaRezerwacji
    extra = 3


class PokojInline(admin.TabularInline):
    model = PokojNaRezerwacji
    extra = 1
    max_num = 3


class RezerwacjaAdmin(admin.ModelAdmin):
    inlines = [UslugaInline, PokojInline]
    list_display = ('nazwisko', 'poczatek_pobytu', 'koniec_pobytu', 'pokoje_verbose')
    fieldsets = [
        (None, {'fields': ['poczatek_pobytu', 'koniec_pobytu', 'nazwisko', 'email', 'telefon', 'dodatkowe_instrukcje']}),
        (None, {'fields': ['kod', 'notatka']}),
        (None, {'fields': ['cena_dorosly', 'cena_dziecko', 'zarchiwizowany']})
    ]

    def queryset(self, request):
        qs = super(RezerwacjaAdmin, self).queryset(request)
        qs = qs.filter(zarchiwizowany=False, koniec_pobytu__gt=datetime.date.today())
        return qs


# JEDZENIE

class JedzenieInline(TranslationStackedInline):
    model = Jedzenie
    extra = 1


class KategoriaJedzeniaAdmin(TranslationAdmin):
    inlines = [JedzenieInline]


# POKOJE ZE ZDJECIAMI

class ZdjecieInline(admin.StackedInline):
    model = ZdjeciaPokojow
    extra = 2


class PokojAdmin(TranslationAdmin):
    inlines = [ZdjecieInline]
    list_display = ('__unicode__', 'dostepnosc')


# OPIS HOTELU

class OpisHoteluAdmin(TranslationAdmin):
    fieldsets = [
        (_('Opis hotelu'), {'fields': ['opis_hotelu', 'zdjecie', 'opis_google']}),
        (_('Naglowek'), {'fields': ['logo', 'tekst_logo', 'tekst_logo_widoczny', 'uklad']}),
        (_('Mapa'), {'fields': ['html_mapy_google', 'wyswietlaj_mape']}),
        (_('Informacje kontaktowe'), {'fields': ['email', 'skype', 'gadu_gadu', 'adres', 'telefon']}),
        (_('Portale spolecznosciowe'), {'fields': ['facebook', 'twitter']})
    ]

    def has_add_permission(self, request):
        if OpisHotelu.objects.count() >= 1:
            return False
        else:
            return True


# USLUGI

class UslugaAdmin(TranslationAdmin):
    list_display = ('nazwa', 'wewnetrzna', 'dostepnosc')


admin.site.register(Rezerwacja, RezerwacjaAdmin)
admin.site.register(Pokoj, PokojAdmin)
admin.site.register(CenaPokoju)
admin.site.register(Usluga, UslugaAdmin)
admin.site.register(KategoriaJedzenia, KategoriaJedzeniaAdmin)
admin.site.register(OpisHotelu, OpisHoteluAdmin)
admin.site.register(ZdjeciaHotelu)
admin.site.register(Newsletter)

# Wiadomosci finalnie nie beda edytowane w panelu admina tylko bedziemy mieli ta strone dla pracownika
# w ktorej pracownike bedzie odpowiadal na wiadomosci i tyle, ale obecnie dodaje to do panelu
# admina zebysmy mogli recznie wstawiac i edytowac wiadomosci do testow
admin.site.register(Wiadomosc)