'''
Created on 26 Feb, 2014

@author: NUSPA
'''
from django.conf.urls import patterns, url

from web.views import *


urlpatterns = patterns('',
    url(r'^$', newcategory),
    url(r'^index/$', newcategory, name="index"),
    url(r'^index/submit', submitcategory, name="submitcat"),
    url(r'^analysis/$', analysis, name="analysis"),
    url(r'^analysis/submit', submitanalysis, name="submitanalysis"),
    url(r'^analysis/delete', deleteSVM, name="deletesvm"),
    url(r'^results/$', results, name="results"),
    url(r'^results/submitgt$', resultssubmitgt, name="resultsgt"),
    
    # debug
    url(r'^parser/$', parserresults),
    url(r'^parserSA/', parserSA),
    url(r'^catresults/', catresults),
    url(r'^classifierresults/', classifierresults),
    url(r'^sentiwordnet/', sentiwordnet),
    url(r'^sentiwordnetdb/', sentiwordnetdb),
    url(r'^keyinfoSA/', keyinfoSA),
    url(r'^slangdict/', slangdict),
    url(r'^doa/', doa),
    url(r'^emoticons', emoticons),
    url(r'eval', evalu)
)
