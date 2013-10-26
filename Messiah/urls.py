from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/Hotel/', include('Hotel.urls_admin', namespace='admin_custom')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('Hotel.urls', namespace='hotel'))
)