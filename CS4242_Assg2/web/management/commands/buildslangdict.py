'''
Created on 6 Mar, 2014

@author: simkerncheh
'''
import codecs
import json
import re
import string
import warnings

from django.core.management.base import BaseCommand
from lxml import html
import requests

from CS4242_Assg2.constants import SLANG_DICT, PATH_SLANG_HASHMAP
from web.models import StorageDict


class Command(BaseCommand):
    
    def __init__(self):
        super(Command, self).__init__()
        self.urls = []
        basis = 'http://www.noslang.com/dictionary/'
        self.urls.append("%s%s/" % (basis, 1))
        
        for letter in string.lowercase:
            self.urls.append("%s%s/" % (basis, letter))
        
        self.uncensorDict = {
                             'f**k' : 'fuck',
                             'b***h': 'bitch',
                             'b***hes': 'bitches',
                             'b*****ds': 'bastard',
                             'c**t': 'cunt',
                             'a**': 'ass',
                             'a**h**e': 'asshole',
                             's**t': 'shit',
                             'f**ker': 'fucker',
                             'f**ked': 'fucked',
                             'f**king': 'fucking',
                             'd**n': 'damn',
                             'motherf**ker': 'motherfucker',
                             'motherf**king': 'motherfucking',
                             'c**k': 'cock',
                             'b*****d': 'bastard',
                             'mothaf**ka': 'motherfucker',
                             'd**k': 'dick',
                             'p***y': 'pussy',
                             'w***e': 'whore',
                             'f**kin': 'fucking',
                             'f**': 'fag',
                             'bulls**t': 'bullshit',
                             'f*ck': 'fuck',
                             'n***a': 'nigger',
                             'cla**': 'class',
                             'dumba**': 'dumbass',
                             'd****ebag': 'douchebag',
                             'n****r': 'nigger',
                             'pa**': 'pass',
                             'ma**': 'mass',
                             's**tty': 'slutty',
                             'motherf**king': 'motherfucking',
                             'f**ken': 'fuck',
                             'c**': 'cum'
                             }
    
    def handle(self, *args, **kwargs):
        resultant_map = {}
        for url in self.urls:
            f = requests.get(url)
            tree = html.fromstring(f.text)
            l1 = tree.xpath('//dl')

            for item in l1:

                l2 = item.xpath('//strong')
                l3 = item.xpath('//dd')
                if len(l2) == len(l3):
                    for idx, item2 in enumerate(l2):
                        uncensored_term = l3[idx].text.lower()
                        for word in re.split(r'\s|[!"#$%&\'()+,-./:;<=>?@[\]^_`{|}~]', uncensored_term):
#                             print word
                            # attempt to replace censored vulgarities
                            if word in self.uncensorDict:
                                uncensored_term = uncensored_term.replace(word, self.uncensorDict[word])
                        resultant_map[u'%s' % (item2.text)] = u'%s' % (uncensored_term)
                        
                        print "%s -- %s" % (item2.text, uncensored_term)
                else:
                    warnings.warn("Data Mismatch in %s" % (url))
                    
        sd = StorageDict(key=SLANG_DICT, stored_dict=resultant_map)
        sd.save()
    
    def saveSlangDictToFile(self, filename):
        slangdict = StorageDict.objects.get(key=SLANG_DICT).stored_dict
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            json.dump(slangdict, f)
    
    def loadSlangDictFromFile(self, filename):
        with codecs.open(filename, encoding='utf-8') as f:
            for line in f:
                slangdict = json.loads(line)
        return slangdict
    
    def saveSlangDictToDb(self, filename):
        '''
        filename : filename of file to save
        '''
        with codecs.open(filename, encoding='utf-8') as f:
            for line in f:
                slangdict = json.loads(line)
        
        sd = StorageDict(key=SLANG_DICT, stored_dict=slangdict)
        sd.save()
        print sd.stored_dict
        
    def getSlangDict(self):
        return StorageDict.objects.get(key=SLANG_DICT).stored_dict

def loadSlangDict():
    sd = StorageDict.objects.get(key=SLANG_DICT).stored_dict
    filter = []
    for k, v in sd.iteritems():
        if len(k) < 3:
            filter.append(k)
    for key in filter:
        sd.pop(key)
    return sd
        
if __name__ == "__main__":
    Command().saveSlangDictToFile(PATH_SLANG_HASHMAP)