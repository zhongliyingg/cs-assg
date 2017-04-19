'''
Created on 13 Mar, 2014

@author: simkerncheh
'''
from django.core.management.base import BaseCommand
from web.helper.DatabaseTools import purgeFeaturesetsFromDB, \
    purgeSVMStatesFromDB
    
class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        purgeFeaturesetsFromDB()
        purgeSVMStatesFromDB()
