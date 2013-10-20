from django.contrib import admin

from Hotel.models import Rezerwacja, Pokoj, Usluga, UslugaNaRezerwacji, PokojNaRezerwacji
from django.core import urlresolvers


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
