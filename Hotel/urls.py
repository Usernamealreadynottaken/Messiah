from django.conf.urls import patterns, include, url

from Hotel import views

urlpatterns = patterns('',
    url(r'^$', views.glowna, name='glowna'),
    url(r'^rezerwacje/$', views.rezerwacje, name='rezerwacje'),
    url(r'^rezerwacje/sprawdz/', views.rezerwacje_sprawdz, name='rezerwacje_sprawdz'),
    url(r'^rezerwacje/wyslij/', views.rezerwacje_wyslij, name='rezerwacje_wyslij')
    # url(r'^wiadomosci/$', views.wiadomosci, name='wiadomosci')
)