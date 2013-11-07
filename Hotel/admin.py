from django.contrib import admin

from Hotel.models import Rezerwacja, Pokoj, Usluga, UslugaNaRezerwacji, PokojNaRezerwacji, Wiadomosc, KategoriaJedzenia, Jedzenie, \
    ZdjeciaPokojow, CenaPokoju, OpisHotelu


# REZERWACJE

class UslugaInline(admin.TabularInline):
    model = UslugaNaRezerwacji
    extra = 3


class PokojInline(admin.TabularInline):
    model = PokojNaRezerwacji
    extra = 1


class RezerwacjaAdmin(admin.ModelAdmin):
    inlines = [UslugaInline, PokojInline]


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

# Wiadomosci finalnie nie beda edytowane w panelu admina tylko bedziemy mieli ta strone dla pracownika
# w ktorej pracownike bedzie odpowiadal na wiadomosci i tyle, ale obecnie dodaje to do panelu
# admina zebysmy mogli recznie wstawiac i edytowac wiadomosci do testow
admin.site.register(Wiadomosc)