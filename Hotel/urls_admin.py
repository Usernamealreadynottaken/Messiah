from django.conf.urls import patterns, include, url

from Hotel import views

urlpatterns = patterns('',
    url(r'^wiadomosci/$', views.wiadomosci, name='wiadomosci'),
    url(r'^wiadomosci/(?P<pk>\d+)/$', views.wyslij_email, name='wyslij_email'),
    url(r'^wiadomosci/oznacz/$', views.wiadomosci_oznacz, name='wiadomosci_oznacz'),
    url(r'^wiadomosci/oznacz/(?P<pk>\d+)/$', views.wiadomosci_oznacz, name='wiadomosci_oznacz_pk'),
    url(r'^archiwum/$', views.archiwum, name='archiwum'),
    url(r'^biuletyn/$', views.biuletyn, name='biuletyn'),
    url(r'^biuletyn/wyslij/$', views.wyslij_biuletyn, name='wyslij_biuletyn')
)