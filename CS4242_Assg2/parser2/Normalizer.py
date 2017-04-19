'''
Created on Jan 27, 2014

@author: administrator
'''
from CS4242_Assg2.settings import BASE_DIR
from django.core.serializers.json import DjangoJSONEncoder
import codecs
import json

class Normalizer():
    
    def __init__(self):
        self.normalize_map = None
        with codecs.open(BASE_DIR + '/parser2/emnlp_json.txt', encoding='utf-8') as f1:
            for line in f1:
                self.normalize_map = json.loads(line, encoding='utf-8')
    
    def normalizeTweet(self, tweet):
        words = tweet.split()
        for index, word in enumerate(words):
            if word in self.normalize_map:
                words[index] = self.normalize_map[word]
        return words
    
    def normalizeTweetFull(self, tweet):
        words = tweet.split()
        for index, word in enumerate(words):
            if word in self.normalize_map:
                words[index] = self.normalize_map[word]
        
        return ' '.join(words)
    
    def normalizeTweetWord(self, word):
        if word in self.normalize_map:
            word = self.normalize_map[word]
        return word
    
    def canNormalize(self,word):
        canNorm = False
        if word in self.normalize_map:
            canNorm = True
        return canNorm
        

if __name__ == '__main__':
    inputFileName = 'emnlp_dict.txt'
    hashmap = {}
    with codecs.open(inputFileName, encoding='utf-8') as k:
        for line in k:
            words = line.split()
            hashmap[words[0]] = words[1]
             
    with codecs.open('emnlp_json.txt', 'w', encoding='utf-8') as f1:
        f1.write(json.dumps(hashmap, cls=DjangoJSONEncoder))

#     with codecs.open('emnlp_json.txt', encoding='utf-8') as f1:
#         for line in f1:
#             json = json.loads(line, encoding='utf-8')
#             print json
