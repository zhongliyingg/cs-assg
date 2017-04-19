# -*- coding: utf-8-*-
'''
Created on 11 Mar, 2014

@author: simkerncheh
'''
from django.core.management.base import BaseCommand
from lxml import html
from web.models import EmoticonMining, EmoticonMiningIntermediate, StorageDict
import codecs
import json
import requests
from CS4242_Assg2.constants import *
from django.core import serializers
class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        mylist = {}
        EmoticonMining.objects.all().delete()
        with codecs.open(PATH_EMOTICONS_DICT, encoding='utf-8') as f:
            for obj in serializers.deserialize("json", f):
                mylist[obj.object.emoticon] = {EMOTICON_DESCRIPTION:obj.object.description, EMOTICON_POLARITY:obj.object.polarity}
                obj.save()
        
        StorageDict.objects.create(key=EMOTICONS_DICT, stored_dict=mylist)
        print mylist
        
    def mine(self, *args, **kwargs):
        templist = []
        descriptionlist = []
        
        url = "http://en.wikipedia.org/wiki/List_of_emoticons"
        f = requests.get(url)
        tree = html.fromstring(f.text)
        l1 = tree.xpath("//table[@class='wikitable']")
        
        for idx, item in enumerate(l1):
            if idx == 0:
                l2 = item.xpath("tr/td")
                
#                 print len(l2)
                go = True
                for item2 in l2:
                    codelist = item2.xpath("code")
                    if len(codelist) == 1:
                        for idx, code in enumerate(codelist):
                            if go:
                                newtext = code.text.replace(u'\xa0', u' ')
                                templist.append({'emoticon_string': newtext, 'desc': ''})
                    
                    else:
                        desc_list = item2.xpath("../descendant::*[not(self::code)]/text()[not(ancestor::sup)]")
                        description = ''.join(desc_list)
                        descriptionlist.append(u"%s" % description)
                    go = not go
                    
        for idx, items in enumerate(descriptionlist):
            templist[idx]['desc'] = items
        
        for item in templist:
            EmoticonMiningIntermediate.objects.create(emoticon_string=item['emoticon_string'], description=item['desc'])
    
    def finalize(self):
        finallist = []
        
        templist = EmoticonMiningIntermediate.objects.all()
        
        for item in templist:
            desc = item.description
            splitted = item.emoticon_string.split()
            for emoticon in splitted:
                finallist.append({'emoticon': emoticon, 'desc': desc, 'pol': item.polarity})
        
        print finallist
        
        for item in finallist:
            EmoticonMining.objects.create(emoticon=item['emoticon'], description=item['desc'], polarity=item['pol'])
    
    def dumptofile(self, filename):
        JSONserializer = serializers.get_serializer("json")
        json_serializer = JSONserializer()
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            json_serializer.serialize(EmoticonMining.objects.all(), stream=f)
              
if __name__ == "__main__":
#     print json.dumps(StorageDict.objects.get(key=EMOTICONS_DICT).stored_dict)
    com = Command()
    StorageDict.objects.filter(key=EMOTICONS_DICT).delete()
    com.dumptofile(PATH_EMOTICONS_DICT)
    com.handle()
    pass
