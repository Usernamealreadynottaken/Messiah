from django.conf.urls import patterns, include, url

from Hotel import views

urlpatterns = patterns('',
    url(r'^wiadomosci/$', views.wiadomosci)
)