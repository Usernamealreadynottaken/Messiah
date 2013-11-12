from django.conf.urls import patterns, include, url

from Hotel import views

urlpatterns = patterns('',
    url(r'^$', views.glowna, name='glowna'),
    url(r'^cennik/$', views.cennik, name='cennik'),
    url(r'^kontakt/$', views.kontakt, name='kontakt'),

    url(r'^rezerwacje/$', views.rezerwacje, name='rezerwacje'),
    url(r'^rezerwacje/sprawdz/$', views.rezerwacje_sprawdz, name='rezerwacje_sprawdz'),
    url(r'^rezerwacje/wyslij/$', views.rezerwacje_wyslij, name='rezerwacje_wyslij'),
    url(r'^rezerwacje/(?P<code>[a-zA-Z0-9]{1,12})/$', views.rezerwacje_kod, name='rezerwacje_kod'),
    url(r'^rezerwacje/sprawdz/(?P<code>[a-zA-Z0-9]{1,12})/$', views.rezerwacje_sprawdz_kod, name='rezerwacje_sprawdz_kod'),
    url(r'^rezerwacje/wyslij/(?P<code>[a-zA-Z0-9]{1,12})/$', views.rezerwacje_wyslij_kod, name='rezerwacje_wyslij_kod'),
    url(r'^rezerwacje/anuluj/(?P<code>[a-zA-Z0-9]{1,12})/$', views.rezerwacje_anuluj, name='rezerwacje_anuluj_kod'),
    url(r'^rezerwacje/anuluj/$', views.rezerwacje_anuluj, name='rezerwacje_anuluj'),
    url(r'^rezerwacjeistnieje/$', views.rezerwacje_istnieje, name='rezerwacje_istnieje'),
    url(r'^rezerwacje/sprawdzemail/(?P<email>.+)/$', views.rezerwacje_sprawdz_email,
        name='rezerwacje_sprawdz_email_email'),
    url(r'^rezerwacje/sprawdzemail/$', views.rezerwacje_sprawdz_email, name='rezerwacje_sprawdz_email'),

    url(r'^wizualizacja/$', views.wizualizacja, name='wizualizacja'),
    url(r'^wizualizacja/(?P<pk>\d+)/$', views.wizualizacja_galeria, name='wizualizacja_galeria')
)