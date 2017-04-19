from dajaxice.core import dajaxice_config
from dajaxice.core.Dajaxice import dajaxice_autodiscover
from django.conf.urls import patterns, url, include
from web.views import *

dajaxice_autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^dajaxice/', include('dajaxice.urls')),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'^', include('web.urls')),
    
)
