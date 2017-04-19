'''
Created on 10 Mar, 2014

@author: simkerncheh
'''
from django.core.management.base import BaseCommand
import codecs
from CS4242_Assg2.constants import PATH_DOA, PLEASANTNESS, ACTIVATION, IMAGERY,\
    DOA_DICT
from web.models import StorageDict

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        newdict = {}
        with codecs.open(PATH_DOA, encoding='utf-8') as f:
            for line in f:
                data = line.split()
                word = data[0]
                ee = data[1]
                aa = data[2]
                ii = data[3]
                
                newee = float(ee)/3
                newdict[word] = {}
                newdict[word][PLEASANTNESS] = newee
                newdict[word][ACTIVATION] = aa
                newdict[word][IMAGERY] = ii
                
        StorageDict.objects.create(key=DOA_DICT, stored_dict=newdict)
                        
if __name__ == '__main__':
    print  StorageDict.objects.get(key=DOA_DICT).stored_dict
