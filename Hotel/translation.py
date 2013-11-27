from modeltranslation.translator import translator, TranslationOptions
from Hotel.models import OpisHotelu, KategoriaJedzenia, Jedzenie, Usluga, Pokoj


class OpisHoteluTO(TranslationOptions):
    fields = ('opis_hotelu', 'opis_google', 'adres', 'tekst_logo')


class KategoriaJedzeniaTO(TranslationOptions):
    fields = ('nazwa', 'opis')


class JedzenieTO(TranslationOptions):
    fields = ('nazwa', 'opis')


class UslugaTO(TranslationOptions):
    fields = ('nazwa', 'opis')


class PokojTO(TranslationOptions):
    fields = ('opis', 'opis_combo')


translator.register(OpisHotelu, OpisHoteluTO)
translator.register(KategoriaJedzenia, KategoriaJedzeniaTO)
translator.register(Jedzenie, JedzenieTO)
translator.register(Usluga, UslugaTO)
translator.register(Pokoj, PokojTO)