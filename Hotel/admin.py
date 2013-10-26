from django.contrib import admin

from Hotel.models import Rezerwacja, Pokoj, Usluga, UslugaNaRezerwacji, PokojNaRezerwacji, Wiadomosc


class UslugaInline(admin.TabularInline):
    model = UslugaNaRezerwacji
    extra = 3


class PokojInline(admin.TabularInline):
    model = PokojNaRezerwacji
    extra = 1


class RezerwacjaAdmin(admin.ModelAdmin):
    inlines = [UslugaInline, PokojInline]


admin.site.register(Rezerwacja, RezerwacjaAdmin)
admin.site.register(Pokoj)
admin.site.register(Usluga)

# Wiadomosci finalnie nie beda edytowane w panelu admina tylko bedziemy mieli ta strone dla pracownika
# w ktorej pracownike bedzie odpowiadal na wiadomosci i tyle, ale obecnie dodaje to do panelu
# admina zebysmy mogli recznie wstawiac i edytowac wiadomosci do testow
admin.site.register(Wiadomosc)