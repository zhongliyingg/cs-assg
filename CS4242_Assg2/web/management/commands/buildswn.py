'''
Created on 2 Mar, 2014

@author: simkerncheh
'''
from CS4242_Assg2.constants import PATH_SENTIWN, SENTIWORDNET_DICT
from django.core.management.base import BaseCommand
from feature_selection.SentiWordNet import SentiWordNetCorpusReader
import os.path
from web.models import StorageDict

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        if os.path.exists(PATH_SENTIWN):
            swn = SentiWordNetCorpusReader(PATH_SENTIWN)
            translationmap = swn.build_senti_translation_map()
            StorageDict.objects.create(key=SENTIWORDNET_DICT, stored_dict=translationmap)
