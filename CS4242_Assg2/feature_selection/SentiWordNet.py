'''
Created on 1 Mar, 2014

@author: Administrator
'''

from nltk.corpus import wordnet as wn
import codecs
import os
import re
import sys
from distutils.log import warn
import warnings
from CS4242_Assg2.constants import TERM_OBJ, TERM_POS_SCORE, TERM_NEG_SCORE

class SentiWordNetCorpusReader:
    def __init__(self, filename):
        """
        Argument:
        filename -- the name of the text file containing the
                    SentiWordNet database
        """        
        self.filename = filename
        self.db = {}
        self.parse_src_file()
        self.pattern_split_synset_terms = re.compile(r'#\d+\s*')
        self.dupeslist = []

    def parse_src_file(self):
        lines = codecs.open(self.filename, "r", "utf8").read().splitlines()
        lines = filter((lambda x : not re.search(r"^\s*#", x)), lines)
        for i, line in enumerate(lines):
            fields = re.split(r"\t+", line)
            fields = map(unicode.strip, fields)
            try:            
                pos, offset, pos_score, neg_score, synset_terms, gloss = fields
            except:
                sys.stderr.write("Line %s formatted incorrectly: %s\n" % (i, line))
            if pos and offset:
                offset = int(offset)
                self.db[(pos, offset)] = (float(pos_score), float(neg_score))

    def senti_synset(self, *vals):        
        if tuple(vals) in self.db:
            pos_score, neg_score = self.db[tuple(vals)]
            pos, offset = vals
            synset = wn._synset_from_pos_and_offset(pos, offset)  # @UndefinedVariable
            return SentiSynset(pos_score, neg_score, synset)
        else:
            synset = wn.synset(vals[0])  # @UndefinedVariable
            pos = synset.pos
            offset = synset.offset
            if (pos, offset) in self.db:
                pos_score, neg_score = self.db[(pos, offset)]
                return SentiSynset(pos_score, neg_score, synset)
            else:
                return None

    def senti_synsets(self, string, pos=None):
        sentis = []
        synset_list = wn.synsets(string, pos)  # @UndefinedVariable
        for synset in synset_list:
            sentis.append(self.senti_synset(synset.name))
        sentis = filter(lambda x : x, sentis)
        return sentis

    def all_senti_synsets(self):
        for key, fields in self.db.iteritems():
            pos, offset = key
            pos_score, neg_score = fields
            synset = wn._synset_from_pos_and_offset(pos, offset)  # @UndefinedVariable
            yield SentiSynset(pos_score, neg_score, synset)
            
    # Added by Kern Cheh
    def build_senti_translation_map(self):
        '''
        Returns:{
            'a': {
                word:
                    'objectivity': 0.0,
                    'positive_score' : 0.0,
                    'negative_score' : 0.0
            }
        }
            
        '''
        returnmap = {}
        
        lines = codecs.open(self.filename, "r", "utf8").read().splitlines()
        lines = filter((lambda x : not re.search(r"^\s*#", x)), lines)
        for i, line in enumerate(lines):
            fields = re.split(r"\t+", line)
            fields = map(unicode.strip, fields)
            try:            
                pos, offset, pos_score, neg_score, synset_terms, gloss = fields
            except:
                sys.stderr.write("Line %s formatted incorrectly: %s\n" % (i, line))
            
            if pos not in returnmap:
                returnmap[pos] = {}
            
            termlist = self.pattern_split_synset_terms.split(synset_terms)
            termlist = filter(None, termlist)
            
            for term in termlist:
                if term not in returnmap[pos]:
                    returnmap[pos][term] = {
                                                TERM_OBJ: 1.0 - (float(pos_score) + float(neg_score)),
                                                TERM_POS_SCORE: float(pos_score),
                                                TERM_NEG_SCORE: float(neg_score),
                                                'occurrences': 1
                                            }
                else:
#                     warnings.warn('Term %s already exists in %s category' % (term, pos))
                    occ = returnmap[pos][term]['occurrences']
                    
                    term_pos_score = returnmap[pos][term][TERM_POS_SCORE]
                    term_neg_score = returnmap[pos][term][TERM_NEG_SCORE]
                    new_pos_score = (term_pos_score * occ) + float(pos_score)
                    new_neg_score = (term_neg_score * occ) + float(neg_score)
                    occ += 1
                    returnmap[pos][term]['occurrences'] = occ
                    returnmap[pos][term][TERM_POS_SCORE] = new_pos_score / occ
                    returnmap[pos][term][TERM_NEG_SCORE] = new_neg_score / occ
                    returnmap[pos][term][TERM_OBJ] = 1.0 - (returnmap[pos][term][TERM_POS_SCORE] + returnmap[pos][term][TERM_NEG_SCORE])
                    
#                     self.dupeslist.append({
#                                                'term': term,
#                                                'pos': pos,
#                                                TERM_OBJ: 1.0 - (float(pos_score) + float(neg_score)),
#                                                TERM_POS_SCORE: pos_score,
#                                                TERM_NEG_SCORE: neg_score
#                                            })
             
                
        return returnmap
######################################################################
            
class SentiSynset:
    def __init__(self, pos_score, neg_score, synset):
        self.pos_score = pos_score
        self.neg_score = neg_score
        self.obj_score = 1.0 - (self.pos_score + self.neg_score)
        self.synset = synset

    def __str__(self):
        """Prints just the Pos/Neg scores for now."""
        s = ""
        s += self.synset.name + "\t"
        s += "PosScore: %s\t" % self.pos_score
        s += "NegScore: %s" % self.neg_score
        return s

    def __repr__(self):
        return "Senti" + repr(self.synset)
                    
######################################################################        

if __name__ == "__main__":
    """
    If run as

    python sentiwordnet.py

    and the file is in this directory, send all of the SentiSynSet
    name, pos_score, neg_score trios to standard output.
    """
    SWN_FILENAME = "SentiWordNet_3.0.0_20130122.txt"
    if os.path.exists(SWN_FILENAME):
        swn = SentiWordNetCorpusReader(SWN_FILENAME)
        swn.build_senti_translation_map()
        print swn.dupeslist
#         for senti_synset in swn.all_senti_synsets():
#             print senti_synset.synset.name, senti_synset.pos_score, senti_synset.neg_score
