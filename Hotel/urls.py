from django.conf.urls import patterns, include, url

from Hotel import views

urlpatterns = patterns('',
    url(r'^$', views.glowna, name='glowna'),
    url(r'^rezerwacje/', views.rezerwacje, name='rezerwacje'),
)