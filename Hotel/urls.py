from django.conf.urls import patterns, include, url

from Hotel import views

urlpatterns = patterns('',
    url(r'^$', views.glowna, name='glowna'),
    url(r'^rezerwacje/$', views.rezerwacje, name='rezerwacje'),
<<<<<<< HEAD
    url(r'^rezerwacje/sprawdz/', views.rezerwacje_sprawdz, name='rezerwacje_sprawdz'),
    url(r'^rezerwacje/wyslij/', views.rezerwacje_wyslij, name='rezerwacje_wyslij')
=======
    url(r'^rezerwacje/check/', views.rezerwacje_check, name='rezerwacje_check'),
    url(r'^wiadomosci/$', views.wiadomosci)
>>>>>>> 0ee5574d7b041b8219488072a1648059562409c7
)