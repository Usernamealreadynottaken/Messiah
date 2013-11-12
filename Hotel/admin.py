from django.contrib import admin
import datetime

from Hotel.models import Rezerwacja, Pokoj, Usluga, UslugaNaRezerwacji, PokojNaRezerwacji, Wiadomosc, KategoriaJedzenia, Jedzenie, \
    ZdjeciaPokojow, CenaPokoju, OpisHotelu, ZdjeciaHotelu, RezerwacjaForm


# REZERWACJE

class UslugaInline(admin.TabularInline):
    model = UslugaNaRezerwacji
    extra = 3


class PokojInline(admin.TabularInline):
    model = PokojNaRezerwacji
    extra = 1


class RezerwacjaAdmin(admin.ModelAdmin):
    inlines = [UslugaInline, PokojInline]
    form = RezerwacjaForm

    def queryset(self, request):
        qs = super(RezerwacjaAdmin, self).queryset(request)
        qs = qs.filter(zarchiwizowany=False, koniec_pobytu__gt=datetime.date.today())
        return qs


# JEDZENIE

class JedzenieInline(admin.StackedInline):
    model = Jedzenie
    extra = 3


class KategoriaJedzeniaAdmin(admin.ModelAdmin):
    inlines = [JedzenieInline]


# POKOJE ZE ZDJECIAMI

class ZdjecieInline(admin.StackedInline):
    model = ZdjeciaPokojow
    extra = 2


class PokojAdmin(admin.ModelAdmin):
    inlines = [ZdjecieInline]


admin.site.register(Rezerwacja, RezerwacjaAdmin)
admin.site.register(Pokoj, PokojAdmin)
admin.site.register(CenaPokoju)
admin.site.register(Usluga)
admin.site.register(KategoriaJedzenia, KategoriaJedzeniaAdmin)
admin.site.register(OpisHotelu)
admin.site.register(ZdjeciaHotelu)

# Wiadomosci finalnie nie beda edytowane w panelu admina tylko bedziemy mieli ta strone dla pracownika
# w ktorej pracownike bedzie odpowiadal na wiadomosci i tyle, ale obecnie dodaje to do panelu
# admina zebysmy mogli recznie wstawiac i edytowac wiadomosci do testow
admin.site.register(Wiadomosc)