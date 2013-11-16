from django.conf.urls import patterns, include, url

from Hotel import views

urlpatterns = patterns('',
    url(r'^wiadomosci/$', views.wiadomosci, name='wiadomosci'),
    url(r'^wiadomosci/(?P<id>\d+)/$', views.wyslij_email, name='wyslij_email'),
    url(r'^archiwum/$', views.archiwum, name='archiwum')
)