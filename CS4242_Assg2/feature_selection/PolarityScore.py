'''
Created on Mar 9, 2014

@author: LIYING
'''
import re

from nltk import pos_tag
from nltk.corpus import wordnet as wn

from CS4242_Assg2.constants import *
from web.models import StorageDict


# ======================== POS ======================== #
# n, v, a, s, r
PENN_TO_SENTI_POS_MAP = {
                        'NN': 'n', 'NNP': 'n', 'NNPS': 'n', 'NNS': 'n',
                        'VB': 'v', 'VBD': 'v', 'VBG': 'v', 'VBN': 'v', 'VBP': 'v', 'VBZ': 'v',
                        'JJ': 'a', 'JJR': 'a', 'JJS': 'a',
                        'RB': 'r', 'RBR': 'r', 'RBS': 'r'
                       }

def mapPennToSentiPOS(penn_pos):
    senti_pos = POS_OTHERS
    if penn_pos in PENN_TO_SENTI_POS_MAP:
        senti_pos = PENN_TO_SENTI_POS_MAP[penn_pos]
    return senti_pos

# ======================== WN ======================== #

def getSynonymns(word, pos):
    '''
        word: to get synonymn
        pos: pos mapped to senti_pos (n,v,a,r)
    '''
    word = word.lower()
    
    synonyms_list = []
    if pos == POS_OTHERS:
        synonyms = wn.synsets(word)  # @UndefinedVariable
    else:
        synonyms = wn.synsets(word, pos)  # @UndefinedVariable
    
    for syn in synonyms:
        for ln in syn.lemma_names:
            if ln == word: # word itself
                continue
            if ln in synonyms_list: # remove duplicates
                continue
            if "_" in ln: # phrases 
                continue
            synonyms_list.append(ln)
    
    return synonyms_list

# ======================== SWN ======================== #
def loadSWNFromDB():
    swn_obj = StorageDict.objects.get(key = SENTIWORDNET_DICT)
    return swn_obj.stored_dict

def getPolarityScoreFromSWN(word, pos, swn, polarity):
    pol_score = 0 #assume neutral
    if pos in swn and word in swn[pos]:
        if polarity == POLARITY_POSITIVE:
            pol_score = swn[pos][word]['pos_score']
        elif polarity == POLARITY_NEGATIVE:
            pol_score = -swn[pos][word]['neg_score']
    return pol_score

def getPolarityFromSWN(word, POS, swn):
    polarity = POLARITY_NONE
    word = word.lower()
    if POS in swn:
        if word in swn[POS]:
            pos_score = swn[POS][word]['pos_score']
            objectivity = swn[POS][word]['objectivity']
            neg_score = swn[POS][word]['neg_score']
            max_score = max(pos_score, objectivity, neg_score)
            if max_score == pos_score:
                polarity = POLARITY_POSITIVE
            elif max_score == neg_score:
                polarity = POLARITY_NEGATIVE
            elif max_score == objectivity:
                polarity = POLARITY_NEUTRAL
        else:
            # TODO: find antonyms & synonyms through wordnet
            pass
    return polarity

# ======================== DOA ======================== #
def loadDOAFromDB():
    return StorageDict.objects.get(key=DOA_DICT).stored_dict

def getPolarityScoreFromDOA(word, pos, doa):
    '''
    Returns a score from 0.333 to 1, 0 if word not in DOA
    '''
    score = DOA_NO_POLARITY_SCORE
    
    word = word.lower()
    if word in doa:
        score = doa[word]['pleasantness']
    else:
        word_syn = getSynonymns(word, pos)
        for ws in word_syn:
            if ws in doa:
                score = doa[ws]['pleasantness']
                break    
    return score

def getPolarityFromDOA(polarity_score):
    if polarity_score == DOA_NO_POLARITY_SCORE:
        polarity = POLARITY_NONE
    elif polarity_score < DOA_THRES_POLARITY_NEG:
        polarity = POLARITY_NEGATIVE
    elif polarity_score > DOA_THRES_POLARITY_POS:
        polarity = POLARITY_POSITIVE
    else:
        polarity = POLARITY_NEUTRAL
    return polarity