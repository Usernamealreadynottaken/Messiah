from django.conf.urls import patterns, include, url

from Hotel import views

urlpatterns = patterns('',
    url(r'^$', views.glowna, name='glowna'),
    url(r'^rezerwacje/$', views.rezerwacje, name='rezerwacje'),
    url(r'^rezerwacje/sprawdz/$', views.rezerwacje_sprawdz, name='rezerwacje_sprawdz'),
    url(r'^rezerwacje/wyslij/$', views.rezerwacje_wyslij, name='rezerwacje_wyslij'),
    url(r'^rezerwacje/(?P<code>[a-zA-Z0-9]{1,12})/$', views.rezerwacje_kod, name='rezerwacje_kod'),
    url(r'^rezerwacje/sprawdz/(?P<code>[a-zA-Z0-9]{1,12})/$', views.rezerwacje_sprawdz_kod, name='rezerwacje_sprawdz_kod')
)