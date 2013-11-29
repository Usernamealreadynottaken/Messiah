from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/Hotel/', include('Hotel.urls_admin', namespace='admin_custom')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'i18n/', include('django.conf.urls.i18n')),
    url(r'^', include('Hotel.urls', namespace='hotel'))
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^Messiah/uploadedimg/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))