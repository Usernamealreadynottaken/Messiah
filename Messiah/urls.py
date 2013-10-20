from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
<<<<<<< HEAD
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^', include('Hotel.urls', namespace='hotel')),
                       )
=======
    url(r'^admin/Hotel/', include('Hotel.urls_admin')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('Hotel.urls', namespace='hotel')),
)
>>>>>>> 0ee5574d7b041b8219488072a1648059562409c7
