from django.conf.urls import patterns, include, url

from Hotel import views

urlpatterns = patterns('',
    url(r'^wiadomosci/$', views.wiadomosci, name='wiadomosci'),
    url(r'^archiwum/$', views.archiwum, name='archiwum')
)