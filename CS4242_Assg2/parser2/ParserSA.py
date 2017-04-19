'''
Created on 27 Feb, 2014

@author: simkerncheh


Parser to be used after classification
'''

import codecs
import codecs
from itertools import chain
import json
import json
import math
import re
import re
import string
import unicodedata
import unicodedata

from nltk.corpus import stopwords, stopwords
from nltk.stem.lancaster import LancasterStemmer, LancasterStemmer
from nltk.tag import pos_tag, pos_tag

from CS4242_Assg2.constants import *
from console_debug.debug_methods import debugPrint
from feature_selection.PolarityScore import loadSWNFromDB, getPolarityFromSWN, \
    mapPennToSentiPOS, getPolarityScoreFromSWN, loadDOAFromDB, getPolarityFromDOA, \
    getPolarityScoreFromDOA
from feature_selection.SentiWordNet import SentiWordNetCorpusReader
from parser2.Normalizer import Normalizer
from parser2.ParserCommon import parseLabelFile, addToCountDict, \
    regex_punctuation_html_plus, regex_punctuation_digit2_plus, \
    filterIrrelevantTokens, removePunctuationsAndNumbers, regex_punctuation_digit2, \
    regex_punctuation_plus, regex_RT
from parser2.Tokenizer import Tokenizer
from web.management.commands.buildslangdict import Command, loadSlangDict
from web.models import StorageDict


tokenizer = Tokenizer(preserve_case=True)
stemmer = LancasterStemmer()
normalizer = Normalizer()
# swn = loadSWNFromDB()
doa = loadDOAFromDB()
sd = loadSlangDict()
emo_dict = StorageDict.objects.get(key=EMOTICONS_DICT).stored_dict

def merge_dicts(*dicts): 
    return dict(chain(*[d.iteritems() for d in dicts]))

def organizeDataByCategory(test_filename, combined_results):
    '''
    Organize tweets based on their categories, based on the results
    of the classifier SVM.
    
    Used to prepare tweets for sentimental analysis
    
    Returns:
        {
            'category': [json_tweet, json_tweet],
        }
    '''
    tweets_by_category = {}
    for key in combined_results.iterkeys():
        tweets_by_category[key] = []
    with codecs.open(test_filename, encoding='cp1252') as f:
        for idx, line in enumerate(f):
            for category in combined_results.iterkeys():
                if combined_results[category][idx] == POSITIVE:
                    tweets_by_category[category].append(line)
    
                   
    return tweets_by_category

def isPunctuationNum(token):
    if re.match(regex_punctuation_html_plus, token):
        return True
    elif re.match(regex_punctuation_digit2_plus, token):
        return True
    return False

# =================== Tokenisation ==================== #
def tokeniseTweet(json_data, translate_slang=False, filter_twitter_tokens=True):
    '''
    remove hashtags, url, usermentions, RT 
    '''
    if filter_twitter_tokens:
        tweet_text = filterIrrelevantTokens(json_data)
    else:
        tweet_text = json_data['text']
    tweet_text = unicodedata.normalize('NFKD', tweet_text).encode('ascii', 'ignore')
#     print "original: %s" % tweet_text
    
    if translate_slang:
        tweet_text = translateSingleWordSlangs(tweet_text, sd)
#     print "translated: %s" % tweet_text    
    tokenized_tweet = tokenizer.tokenize(tweet_text)
    
    if filter_twitter_tokens:
        tokenized_tweet = filterUncapturedTwitterTokens(tokenized_tweet)
    return tokenized_tweet

def getUncapturedHashtags(tokenised_tweet_no_filter):
    '''
    tokenised_tweet_no_filter: havent remove the uncaptured twitter tokens
    '''
    uncaptured_ht = []
    for token in tokenised_tweet_no_filter:
        if re.match(r"^#", token):
            token = token[1:]
            if len(token) != 0:
                uncaptured_ht.append(token)
    return uncaptured_ht

def getUncapturedUserMentions(tokenised_tweet_no_filter):
    uncaptured = []
    for token in tokenised_tweet_no_filter:
        if re.match(r"^@", token):
            token = token[1:]
            if len(token) != 0:  # not an @ punctuation
                uncaptured.append(token)
    
    return uncaptured

def isValidUrl(url):
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)

def filterUncapturedTwitterTokens(tokenised_tweet):
    remaining_tweet = []
    
    for token in tokenised_tweet:
        if re.match(r"^#", token):
            continue
        if re.match(r"^@", token):
            continue
        if isValidUrl(token):
            continue
#         if re.match(r'\bRT\b', token, re.IGNORECASE):
#             continue
        remaining_tweet.append(token)
    return remaining_tweet

# =================== Unigrams ==================== #
def getText(tokenised_tweet, negation_flags, use_negation=False):
    feature_text = {FEATURE_COUNT:0, FEATURE_VALUE: {}}
    for word in tokenised_tweet:
        negated = False
        if word in negation_flags and negation_flags[word]:
            negated = True
        if isEmoticon(word, emo_dict):
            continue
        
        is_slang = isSlang(word, sd)
        if is_slang:  
            translated_slang = translateSlangWord(word, sd)
            tokenised_slang = tokenizer.tokenize(translated_slang)
            if len(tokenised_slang) == 1: # translated slang
                split_words = tokenised_slang
                is_slang = False
            else: # don't remove punctuation/numbers
                split_words = [word]
#                 print split_words
                
        if not is_slang:
            split_words = removePunctuationsAndNumbers(word)
        for w in split_words:
            w = w.lower()
            if w in stopwords.words('english'):  # skip stopwords
                continue  
            if not is_slang:  # stem if its not slang
                w = stemmer.stem(w)
            if isFullCaps(word):  # preserve case for words in full
                w = w.upper()
            if use_negation and negated:
                w = "NOT_%s" % w  
#                 print w
            feature_text[FEATURE_COUNT] += 1
            addToCountDict(feature_text[FEATURE_VALUE], w, 1)
    
    # TODO: should we use presence? results will drop abit
#     for text in feature_text[FEATURE_VALUE]:
#         feature_text[FEATURE_VALUE][text] = 1
    return feature_text 

def getHashTags_SA(json_data, tokenised_tweet_no_filter):
    feature_ht = {FEATURE_COUNT:0, FEATURE_VALUE: {}}
    for ht in json_data['entities']['hashtags']:
        feature_ht[FEATURE_COUNT] += 1
        addToCountDict(feature_ht[FEATURE_VALUE], "#HT_" + ht['text'], 1)
    
    for ht in getUncapturedHashtags(tokenised_tweet_no_filter):
        feature_ht[FEATURE_COUNT] += 1
        addToCountDict(feature_ht[FEATURE_VALUE], "#HT_" + ht, 1)
    return feature_ht

def getUserMentions_SA(json_data, tokenised_tweet_no_filter):
    '''
    Get user ids of users mentioned in tweet, include tweeter of tweet
    '''
    feature_obj = {FEATURE_COUNT:0, FEATURE_VALUE: {}}
    for um in json_data['entities']['user_mentions']:
        feature_obj[FEATURE_COUNT] += 1
        addToCountDict(feature_obj[FEATURE_VALUE], "@UM_" + um['id_str'], 1)
#     addToCountDict(feature_obj[FEATURE_VALUE], "@UM_" + str(json_data['user']['id']), 1)
    
    for um in getUncapturedUserMentions(tokenised_tweet_no_filter):
        feature_obj[FEATURE_COUNT] += 1
        addToCountDict(feature_obj[FEATURE_VALUE], "@UM_" + um, 1)
    
    for um in feature_obj[FEATURE_VALUE]:
        feature_obj[FEATURE_VALUE][um] = 1
    return feature_obj

def getTwitterTokenCount(json_data, tokenised_tweet_no_filter):
    feature_obj = {FEATURE_COUNT:0, FEATURE_VALUE: {}}
    for twitter_token, entity in json_data['entities'].iteritems():
        for value in entity:
            feature_obj[FEATURE_COUNT] += 1
            addToCountDict(feature_obj[FEATURE_VALUE], "TWITTER_TOKEN_" + twitter_token, 1)
    
    for token in tokenised_tweet_no_filter:
        if re.match(r"^#", token):
            feature_obj[FEATURE_COUNT] += 1
            addToCountDict(feature_obj[FEATURE_VALUE], 'TWITTER_TOKEN_hashtags', 1)
        if re.match(r"^@", token):
            feature_obj[FEATURE_COUNT] += 1
            addToCountDict(feature_obj[FEATURE_VALUE], 'TWITTER_TOKEN_user_mentions', 1)
        if isValidUrl(token):
            feature_obj[FEATURE_COUNT] += 1
            addToCountDict(feature_obj[FEATURE_VALUE], 'TWITTER_TOKEN_urls', 1)
#     print feature_obj
    return feature_obj

def normaliseTwitterTokens(json_data):    
    norm_twitter_tokens = []
    
    tweet_text_filter = filterIrrelevantTokens(json_data, filter_hashtags=False, filter_user_mentions=False)
    
    tweet_text_norm = unicodedata.normalize('NFKD', tweet_text_filter).encode('ascii', 'ignore')
    tweet_text_translate = normalizer.normalizeTweetFull(tweet_text_norm)
    tweet_text_translate = translateSingleWordSlangs(tweet_text_translate, sd)
    
    tokenised_tweet_no_filter = tokenizer.tokenize(tweet_text_translate)
    for token in tokenised_tweet_no_filter:
        if re.match(r"^#", token):
            token = token[1:]
            if len(token) != 0:
                norm_twitter_tokens.append(token)
        elif re.match(r"^@", token):
            token = token[1:]
            if len(token) != 0:
                norm_twitter_tokens.append(token)
        elif isValidUrl(token):
            continue
        else:
            norm_twitter_tokens.append(token)
    return norm_twitter_tokens

def getTwitterTokenPercentage(twitter_tokens, tweet_text):
    feature_obj = {FEATURE_VALUE: {}}
    tweet_text_norm = unicodedata.normalize('NFKD', tweet_text).encode('ascii', 'ignore')
    tokenised_tweet = tokenizer.tokenize(tweet_text_norm)
    tweet_length = len(tokenised_tweet)
    twitter_token_count = twitter_tokens[FEATURE_COUNT]
    
    if tweet_length == 0:
        percentage = 0
    else:
        percentage = float(twitter_token_count) / float(tweet_length)
    feature_obj[FEATURE_VALUE]["TWITTER_TOKEN_PERCENTAGE"] = percentage
    print feature_obj
    return feature_obj
    

def flagNegatedWords(tokenised_tweet):
    '''
        ( 0: [negation_words], 1: [negated_flags])
    '''
    negated_tweet = []
    negated_flags = {}
    negation_words = []
    negation = r"\b(no|not|cannot|\w*n't|never)\b"
    regex_negation = re.compile(negation, re.IGNORECASE)
    append_not = False
    for token in tokenised_tweet:
        token = token.lower()
        
        if append_not:
            if re.match(regex_punctuation_plus, token):
                negated_flags[token] = False   
                append_not = False  # stop appending if matched punctuation 
                  
#             elif re.match(r"^#", token) or re.match(r"^@", token) or isValidUrl(token):
#                 negated_flags[token] = False   
#                 append_not = False # stop appending if matched twitter tokens
                
            else:
                negated_flags[token] = True  
                token = "NOT_%s" % token  # appending
                
        elif re.match(regex_negation, token):
            negated_flags[token] = False 
            negation_words.append(token)
            append_not = True  # start appending if matched negation word
            
        else:
            negated_flags[token] = False  
            
        negated_tweet.append(token) 

    return negation_words, negated_flags

# =================== Slangs ==================== #
def isSlang(word, sd):
    isSlang = False
    word = word.lower()
    if word in sd:
        isSlang = True
    return isSlang

def translateSlangWord(word, sd):
    '''
        Translate single slang word using slang dict
        Translated word may be a phrase separated by whitespace
        Preserve casing of word e.g. LOL: LAUGHING OUT LOUD, Lol:Laughing out loud
        Return original word if not translated
    '''
    translated_slang = word
    word_lowered = word.lower()
    if word_lowered in sd:
        translated_slang = sd[word_lowered]
#         print word, translated_slang
        if word.isupper():
            translated_slang = translated_slang.upper()
        if word.istitle():
            translated_slang = translated_slang.title()
        
    return translated_slang

def getSlangs(tweet_text, sd):
    tokenised_tweet = tweet_text.split()
    for token in tokenised_tweet:
        token_lowered = token.lower()
        if token_lowered in sd:
            slang_split = sd[token_lowered].split()
            print token_lowered, slang_split
#             for slang in slang_split:
#                 print slang


def translateSingleWordSlangs(tweet_text, sd):
    translated_tokens = []
    #may not capture some words with appended punct, handled when getText
    tokenised_tweet = tweet_text.split() 
    for token in tokenised_tweet:
        translated_slang = translateSlangWord(token, sd)
        tokenised_translated_slang = re.split(r'\s+', translated_slang)
#         for token_slang in tokenised_translated_slang: # result in wrong translations
#             translated_tokens.append(token_slang)
            
        if len(tokenised_translated_slang) == 1:
            word = translated_slang
        else:
            word = token
        translated_tokens.append(word)
        
    translated_tweet = " ".join(translated_tokens)
#     print tweet_text
#     print translated_tweet
    return translated_tweet
    
def translateSlangs(tweet_text, sd):
    translated = False
    translated_list = []
    translated_tokens = []
    tokenised_tweet = tweet_text.split()
    for token in tokenised_tweet:
        token_lowered = token.lower()
        if token_lowered in sd:
            translated = True
            slang_split = sd[token_lowered].split()
            for slang in slang_split:
                translated_tokens.append(slang)
                translated_list.append(slang)
        else:    
            translated_tokens.append(token)
    
    translated_tweet = " ".join(translated_tokens)
#     if translated:
#         print "original: %s" % tweet_text
#         print "translated: %s" % translated_tweet
#         print "translated list: %s" % translated_list
    
    return translated_tweet

# =================== Exclamation ==================== #
def getExclamationPrescence(tokenised_tweet):
    feature_obj = {FEATURE_VALUE:{}}
    has_exclamation = 0
    for token in tokenised_tweet:
        if re.search(r"!", token):
            has_exclamation = 1
            break
    feature_obj[FEATURE_VALUE]["EXCLAMATION_PRESENCE"] = has_exclamation
    return feature_obj

def getExclamationCount(tokenised_tweet):
    feature_obj = {FEATURE_VALUE:{}}
    count_exclamation = 0
    for token in tokenised_tweet:
        result = re.findall(r'!', token)
        if result:
            count_exclamation += len(result)
    feature_obj[FEATURE_VALUE]["EXCLAMATION_COUNT"] = count_exclamation
    return feature_obj
        

# =================== Emoticons ==================== #
emoticon_string = r"""
    (?:
      [<>]?
      [:;=8]                     # eyes
      [\-o\*\']?                 # optional nose
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth      
      |
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      [\-o\*\']?                 # optional nose
      [:;=8]                     # eyes
      [<>]?
    )"""
regex_emoticon = re.compile(emoticon_string, re.VERBOSE | re.I | re.UNICODE)

def isEmoticon(token, emo_dict):
    is_emoticon = False
    if re.match(regex_emoticon, token):
        is_emoticon = True
    elif token in emo_dict:
        is_emoticon = True
    return is_emoticon

def getEmoticonPolarity(emoticon, emo_dict):
    polarity = POLARITY_NONE
    if emoticon in emo_dict:
        polarity = emo_dict[emoticon]['polarity']
    return polarity

def getEmoticons(tokenised_tweet, emo_dict):
    feature_emoticons = {FEATURE_COUNT:0,
                         FEATURE_VALUE: {}}
    for word in tokenised_tweet:
        if isEmoticon(word, emo_dict):
            feature_emoticons[FEATURE_COUNT] += 1
            addToCountDict(feature_emoticons[FEATURE_VALUE], word, 1)
    return feature_emoticons

def getEmoticonPolarityCount(tokenised_tweet, emo_dict):

    feature_emoticons = {FEATURE_COUNT:0,
                         FEATURE_VALUE: {'EMO_V_POS': 0,
                                         'EMO_POS': 0,
                                         'EMO_NEU': 0,
                                         'EMO_NEG': 0,
                                         'EMO_V_NEG': 0}}
    for word in tokenised_tweet:
        if word in emo_dict:
            polarity = getEmoticonPolarity(word, emo_dict)
            if polarity == POLARITY_VERY_POSITIVE:
                feature_emoticons[FEATURE_COUNT] += 1
                addToCountDict(feature_emoticons[FEATURE_VALUE], 'EMO_V_POS', 1)
            elif polarity == POLARITY_POSITIVE:
                feature_emoticons[FEATURE_COUNT] += 1
                addToCountDict(feature_emoticons[FEATURE_VALUE], 'EMO_POS', 1)
            elif polarity == POLARITY_NEUTRAL:
                feature_emoticons[FEATURE_COUNT] += 1
                addToCountDict(feature_emoticons[FEATURE_VALUE], 'EMO_NEU', 1)
            elif polarity == POLARITY_NEGATIVE:
                feature_emoticons[FEATURE_COUNT] += 1
                addToCountDict(feature_emoticons[FEATURE_VALUE], 'EMO_NEG', 1)
            elif polarity == POLARITY_VERY_NEGATIVE:
                feature_emoticons[FEATURE_COUNT] += 1
                addToCountDict(feature_emoticons[FEATURE_VALUE], 'EMO_V_NEG', 1)

#             addToCountDict(feature_emoticons[FEATURE_VALUE], word, 1)
#     print feature_emoticons
    return feature_emoticons

def loadEMODictFromDB():
    return StorageDict.objects.get(key=EMOTICONS_DICT).stored_dict

# =================== Capitalised Text ==================== #
def isFullCaps(token):
    split_words = removePunctuationsAndNumbers(token)
    token = ''.join(split_words)
    
    isFullCaps = True
    if len(token) == 0:
        isFullCaps = False
    else:
        for t in u"%s" % token:
            if not t.isupper():
                isFullCaps = False
                break
    return isFullCaps

def getCapitalisedText(tokenised_tweet):
    feature_caps = {FEATURE_COUNT:0, FEATURE_VALUE: {}}
    for word in tokenised_tweet:
#         split_words = removePunctuationsAndNumbers(word)
#         for w in split_words:
        if isFullCaps(word):
            feature_caps[FEATURE_COUNT] += 1
            addToCountDict(feature_caps[FEATURE_VALUE], word, 1)
    return feature_caps

def getCapitalisedTextPresence(cap_text):
    feature_obj = {FEATURE_VALUE: {}}
    if cap_text[FEATURE_COUNT] == 0:
        caps_presence = 0
    else:
        caps_presence = 1
    feature_obj[FEATURE_VALUE]["CAPS_PRESENCE"] = caps_presence
    return feature_obj

def getCapitalisedTextPolarityCount(cap_text, tweet_word_polarity): 
    feature_pol = {FEATURE_COUNT:0, FEATURE_VALUE: {}}
    for word in cap_text[FEATURE_VALUE]:
        word_polarity = getPolarityOfWord(word, tweet_word_polarity)
        if word_polarity == POLARITY_POSITIVE:
            feature_pol[FEATURE_COUNT] += 1
            addToCountDict(feature_pol[FEATURE_VALUE], "POLARTITY_CAPS_POS", 1)
        if word_polarity == POLARITY_NEGATIVE:
            feature_pol[FEATURE_COUNT] += 1
            addToCountDict(feature_pol[FEATURE_VALUE], "POLARTITY_CAPS_NEG", 1)
        if word_polarity == POLARITY_NEUTRAL:
            feature_pol[FEATURE_COUNT] += 1 
            addToCountDict(feature_pol[FEATURE_VALUE], "POLARTITY_CAPS_NEU", 1)
    return feature_pol

def getCapitalisedTextPercentage(cap_text, tokenised_tweet):
    feature_obj = {FEATURE_VALUE: {}}
    
#     tweet_text_norm = unicodedata.normalize('NFKD', tweet_text).encode('ascii', 'ignore')
#     tokenised_tweet = tokenizer.tokenize(tweet_text_norm)
    
    len_tweet = len(tokenised_tweet)
    len_cap_text = cap_text[FEATURE_COUNT]
    

    if len_tweet == 0:
        percentage = 0
    else:
        percentage = float(len_cap_text) / float(len_tweet)
    feature_obj[FEATURE_VALUE]["CAPS_PERCENTAGE"] = percentage
    return feature_obj

# =================== Capitalised Text END ==================== #


# =================== Parts of Speech ==================== #

def tagSentiPOS(tokenised_tweet):
    pos_tagged_tweet = pos_tag(tokenised_tweet)
        
    senti_pos_tagged_tweet = {}
    for word, penn_pos in pos_tagged_tweet:
#         if isSlang(word, sd):
#             word_translated = translateSlangWord(word, sd)
#             tokenise_word_translated = tokenizer.tokenize(word_translated)
        senti_pos = mapPennToSentiPOS(penn_pos)
        senti_pos_tagged_tweet[word] = senti_pos
        
    return senti_pos_tagged_tweet

def getPosFeatures(pos_tagged_tweet):
    '''
    {
        FEATURE_COUNT: number of POS (a,n,v,r,other) features in tweet
        FEATURE_VALUE: {pos_tag: number of pos_tag features in tweet}
    }
    '''
    feature_pos = {FEATURE_COUNT:0, FEATURE_VALUE: {}}
    for word, pos in pos_tagged_tweet.iteritems():
        if pos != POS_OTHERS:
            feature_pos[FEATURE_COUNT] += 1
            addToCountDict(feature_pos[FEATURE_VALUE], "POS_TAG_%s" % pos, 1)
    return feature_pos

# =================== Parts of Speech END ==================== #


# =================== Polarity Information ==================== #
def getPolarityScoreForSlang(word, sd):
    word_translated = translateSlangWord(word, sd)
    tokenise_word_translated = tokenizer.tokenize(word_translated)
    pos_word_translated = tagSentiPOS(tokenise_word_translated)
#             print pos_word_translated
    word_translated_polarity_score = []
    for word_trans, pos_trans in pos_word_translated.iteritems():
        w_polarity_score = getPolarityScoreFromDOA(word_trans, pos_trans, doa)
        word_translated_polarity_score.append(w_polarity_score)
#             print word_translated_polarity_score
    non_zero_terms = [x for x in word_translated_polarity_score if x > 0]
#             print word, word_polarity_score
#     print word_translated_polarity_score
    if sum(word_translated_polarity_score) == 0:
        word_polarity_score = 0
    neg_score_thres = DOA_THRES_POLARITY_NEG - min(word_translated_polarity_score)
    pos_score_thres = max(word_translated_polarity_score) - DOA_THRES_POLARITY_POS 
    if neg_score_thres > 0 and pos_score_thres > 0: # have very positive & negative term
        if neg_score_thres > pos_score_thres: # more negative term
            word_polarity_score = min(word_translated_polarity_score)
        elif pos_score_thres > neg_score_thres: # more positive term
            word_polarity_score = max(word_translated_polarity_score)
    elif neg_score_thres > 0 and pos_score_thres <= 0: # have very negative term
        word_polarity_score = min(word_translated_polarity_score)
    elif neg_score_thres <= 0 and pos_score_thres > 0: # have very positive term
        word_polarity_score = max(word_translated_polarity_score)
    elif neg_score_thres <= 0 and pos_score_thres <= 0: # all neutral terms
        if len(non_zero_terms)!= 0:
            word_polarity_score = sum(word_translated_polarity_score)/float(len(non_zero_terms))
        else:
            word_polarity_score = 0
#             print word, word_polarity_score
    return word_polarity_score

def getPolarityInformationOfTweet(pos_tagged_tweet, negation_flags, use_negation=False):
    '''
    Return: Polarity Information
    {
        POLARITY_WORD: { word: polarity },
        POLARITY_SCORES_WORD: { word: polarity score}
    }
    '''
    polarity_obj = {POLARITY_WORD: {},
                    POLARITY_SCORES_WORD: {}}
    for word, pos in pos_tagged_tweet.iteritems():
#         if isSlang(word, sd):
#             word_polarity_score = getPolarityScoreForSlang(word, sd)
#         else:    
        word_polarity_score = getPolarityScoreFromDOA(word, pos, doa)
        if use_negation and word in negation_flags and negation_flags[word]:
            if word_polarity_score != 0:  # word has polarity
                # inverse score = (1+0.333) - original score
                word_polarity_score = float(4.0 / 3.0) - word_polarity_score 
        polarity_obj[POLARITY_SCORES_WORD][word] = word_polarity_score
        
        word_polarity = getPolarityFromDOA(word_polarity_score)
        polarity_obj[POLARITY_WORD][word] = word_polarity
    return polarity_obj

def getPolarityOfWord(word, polarity_information):
    word_polarity = POLARITY_NONE
    if word in polarity_information:
        word_polarity = polarity_information[word]
#     print word, word_polarity
    return word_polarity

def getPolarityScoreOfWord(word, polarity_information):
    word_polarity_score = 0
    if word in polarity_information:
        word_polarity_score = polarity_information[word]
    return word_polarity_score

# =================== Polarity Information END ==================== #
    

# =================== Polarity Features ==================== #

def getPolarityScores(pos_tagged_tweet, tweet_word_polarity_scores):
    '''
    {
        FEATURE_VALUE: {
            POLARITY_SCORES_WORD: sum of polarity scores of all words
            POLARITY_SCORES_POS: sum of polarity scores of words of POS
        }
    }
    '''
    
    feature_obj = {FEATURE_VALUE: {}}
    
    word_polarity_score = 0.0
    pos_polarity_score = 0.0
    
    word_count = 0
    pos_count = 0
        
    for word, pos in pos_tagged_tweet.iteritems():
#         word_lower = word.lower()
#         if word_lower in stopwords.words('english'):  # skip stopwords
#             continue  
        word_polarity_score += tweet_word_polarity_scores[word]
        if tweet_word_polarity_scores[word] != 0:
            word_count += 1
        if pos != POS_OTHERS:
            pos_polarity_score += tweet_word_polarity_scores[word]
            if tweet_word_polarity_scores[word] != 0:
                pos_count += 1
        
#     if word_count == 0:
#         word_polarity_score = 0
#     else:
#         word_polarity_score = word_polarity_score/float(word_count)
#           
#     if pos_count == 0:
#         pos_polarity_score = 0
#     else:
#         pos_polarity_score = pos_polarity_score/float(pos_count)
    
    feature_obj[FEATURE_VALUE][POLARITY_SCORES_WORD] = word_polarity_score
    feature_obj[FEATURE_VALUE][POLARITY_SCORES_POS] = pos_polarity_score
#     print feature_obj
    return feature_obj    

def getPolarityScores0(pos_tagged_tweet, tweet_word_polarity_scores):
    '''
    {
        FEATURE_VALUE: {
            POLARITY_SCORES_WORD: sum of polarity scores of all words
            POLARITY_SCORES_POS: sum of polarity scores of words of POS
        }
    }
    '''
    
    feature_obj = {FEATURE_COUNT: 0, FEATURE_VALUE: {}}
    
    word_score_list = []  
    pos_score_list = []

    for word, pos in pos_tagged_tweet.iteritems():
        word_score_list.append(tweet_word_polarity_scores[word])
        if pos != POS_OTHERS:
            pos_score_list.append(tweet_word_polarity_scores[word])
    
    feature_obj[FEATURE_VALUE][POLARITY_SCORES_WORD] = normalisePolarityScore(word_score_list)
    feature_obj[FEATURE_VALUE][POLARITY_SCORES_POS] = normalisePolarityScore(pos_score_list)
#     print feature_obj
    return feature_obj

def normalisePolarityScore(polarity_score_list):
    sum = 0.0
    sum_squares = 0.0
    for score in polarity_score_list:
#         score -= 1.0/3.0
        sum_squares += score*score
    norm_score_denom = math.sqrt(sum_squares)
    
    norm_score_total = 0.0
    if norm_score_denom != 0:
        for score in polarity_score_list:
#             print score, norm_score_denom
            norm_score_total += score/norm_score_denom
            
        norm_score_avg = norm_score_total/len([s for s in polarity_score_list if s > 0])  
#         norm_score_avg = norm_score_total/len(polarity_score_list)     
    else:
        norm_score_avg = 0
    return norm_score_total

def getPolarityScores2(pos_tagged_tweet, tweet_word_polarity_scores):
    '''
    {
        FEATURE_VALUE: {
            POLARITY_SCORES_WORD: sum of polarity scores of all words
            POLARITY_SCORES_POS: sum of polarity scores of words of POS
        }
    }
    '''
    feature_obj = {FEATURE_VALUE: {"POLARITY_SCORES_ALL": 0}}
    
    word_polarity_score = 0.0
    pos_polarity_score = 0.0
    jj_score_list = []  
    nn_score_list = []  
    vb_score_list = []  
    rb_score_list = [] 
    word_score_list = [] 
        
    for word, pos in pos_tagged_tweet.iteritems():  
        word_score_list.append(tweet_word_polarity_scores[word])
        if pos == POS_OTHERS:
            continue
        elif pos == POS_ADJ:
            jj_score_list.append(tweet_word_polarity_scores[word])   
        elif pos == POS_ADV:
            rb_score_list.append(tweet_word_polarity_scores[word])
        elif pos == POS_NOUN:
            nn_score_list.append(tweet_word_polarity_scores[word])
        elif pos == POS_VERB:
            vb_score_list.append(tweet_word_polarity_scores[word])
        
    feature_obj[FEATURE_VALUE][POLARITY_SCORES_WORD] = normalisePolarityScore(word_score_list)
    feature_obj[FEATURE_VALUE]['POLARITY_SCORES_JJ'] = normalisePolarityScore(jj_score_list)
    feature_obj[FEATURE_VALUE]['POLARITY_SCORES_RB'] = normalisePolarityScore(rb_score_list)
    feature_obj[FEATURE_VALUE]['POLARITY_SCORES_NN'] = normalisePolarityScore(nn_score_list)
    feature_obj[FEATURE_VALUE]['POLARITY_SCORES_VB'] = normalisePolarityScore(vb_score_list)
    return feature_obj    

def getPolarityTextCount(pos_tagged_tweet, tweet_word_polarity):
    '''
    {
        FEATURE_COUNT: number of text features with polarity
        FEATURE_VALUE: {text: polarity score of text}
    }
    '''
    
    feature_pol = {FEATURE_COUNT:0, FEATURE_VALUE: {}}
    
    for word, pos in pos_tagged_tweet.iteritems():
        word_polarity = getPolarityOfWord(word, tweet_word_polarity)
        if word_polarity == POLARITY_POSITIVE:
            feature_pol[FEATURE_COUNT] += 1
            addToCountDict(feature_pol[FEATURE_VALUE], "POLARITY_TEXT_POS", 1)
        elif word_polarity == POLARITY_NEGATIVE:
            feature_pol[FEATURE_COUNT] += 1
            addToCountDict(feature_pol[FEATURE_VALUE], "POLARITY_TEXT_NEG", 1)
        elif word_polarity == POLARITY_NEUTRAL:
            feature_pol[FEATURE_COUNT] += 1
            addToCountDict(feature_pol[FEATURE_VALUE], "POLARITY_TEXT_NEU", 1)

    return feature_pol

def getPolarityPosCount(pos_tagged_tweet, tweet_word_polarity):
    '''
    {
        FEATURE_COUNT: number of text features of POS (a,n,v,r) with polarity in tweet
        FEATURE_VALUE: {polarity type: number of text features of POS (a,n,v,r) with polarity in tweet}
    }
    '''
    feature_pol = {FEATURE_COUNT:0, FEATURE_VALUE: {}}
    
    for word, pos in pos_tagged_tweet.iteritems():
#         word_polarity = getPolarityFromSWN(word, pos, swn) # empty string if word not found
        if pos == POS_OTHERS:
            continue
        word_polarity = getPolarityOfWord(word, tweet_word_polarity)
        if word_polarity == POLARITY_POSITIVE:
            feature_pol[FEATURE_COUNT] += 1
            addToCountDict(feature_pol[FEATURE_VALUE], "POLARTITY_PoS_POS", 1)
        if word_polarity == POLARITY_NEGATIVE:
            feature_pol[FEATURE_COUNT] += 1
            addToCountDict(feature_pol[FEATURE_VALUE], "POLARTITY_PoS_NEG", 1)
        if word_polarity == POLARITY_NEUTRAL:
            feature_pol[FEATURE_COUNT] += 1
            addToCountDict(feature_pol[FEATURE_VALUE], "POLARTITY_PoS_NEU", 1)
        
    return feature_pol

# =================== Polarity Features END ==================== #

def extractSentiFeaturesFromTweet(json_data, features=FEATURES_SA_DEFAULT):
    '''
    Params:
    json_data: json input line from file
    
    Return:
        {
            TWEET_FULL: 'Do you wanna build a #snowman', 
            TWEET_FEATURES: {
                FEATURE_TEXT: {FEATURE_COUNT: number, FEATURE_VALUE: {feature: count}}, 
                FEATURE_HASHTAGS: {FEATURE_COUNT: number, FEATURE_VALUE: {feature: count}},
                ...
            }
        }
    '''
    features_dict = {}
    tweet_text_filter = filterIrrelevantTokens(json_data)
    tweet_text_norm = unicodedata.normalize('NFKD', tweet_text_filter).encode('ascii', 'ignore')
    
    tweet_text_translate = normalizer.normalizeTweetFull(tweet_text_norm)
    tweet_text_translate2 = translateSingleWordSlangs(tweet_text_translate, sd)
    
    tokenised_tweet_no_filter = tokenizer.tokenize(tweet_text_translate2)
    tokenised_tweet = filterUncapturedTwitterTokens(tokenised_tweet_no_filter)

    pos_tagged_tweet = tagSentiPOS(tokenised_tweet)

#     norm_twitter_tokens_to_words = normaliseTwitterTokens(json_data)
#     pos_tagged_tweet = tagSentiPOS(norm_twitter_tokens_to_words)
    
    negation_info = flagNegatedWords(tokenised_tweet)
    negation_word_count = len(negation_info[0])
    negation_flags = negation_info[1]
            
    tweet_polarity_info = getPolarityInformationOfTweet(
                                pos_tagged_tweet, negation_flags, use_negation=True)
#     features_dict[POLARITY_WORD] = tweet_polarity_info[POLARITY_WORD]
    if json_data['in_reply_to_status_id_str'] != None:
        features_dict[FEATURE_SA_REPLY_TO_ID] = json_data['in_reply_to_status_id_str']
    else:
        features_dict[FEATURE_SA_REPLY_TO_ID] = ""
        
    features_dict[FEATURE_SA_TWEETID_STR] = json_data['id_str']
    
    # === Negation === #
    if FEATURE_SA_NEGATION:  # in use
        features_dict[FEATURE_SA_NEGATION] = {FEATURE_VALUE: 
                                                {'NEGATION_COUNT': negation_word_count}}
    # {FEATURE_VALUE: {'NEGATION_COUNT': int}}
    
    # === Polarity/POS === #
    if FEATURE_SA_POS in features:  # in use
        PoS_feat = getPosFeatures(pos_tagged_tweet)
        features_dict[FEATURE_SA_POS] = PoS_feat
    # {FEATURE_VALUE: {POS_TAG_}}
        
    if FEATURE_SA_POLARITY_POS in features:  # in use
        features_dict[FEATURE_SA_POLARITY_POS] = getPolarityPosCount(
                                                      pos_tagged_tweet,
                                                      tweet_polarity_info[POLARITY_WORD])
        
    if FEATURE_SA_POLARITY_TEXT in features:  # in use
        features_dict[FEATURE_SA_POLARITY_TEXT] = getPolarityTextCount(
                                                      pos_tagged_tweet,
                                                      tweet_polarity_info[POLARITY_WORD])
    
    if FEATURE_SA_POLARITY_SCORES in features:  # in use
        features_dict[FEATURE_SA_POLARITY_SCORES] = getPolarityScores(
                                                      pos_tagged_tweet,
                                                      tweet_polarity_info[POLARITY_SCORES_WORD])
    
    # === Capitalised Text === #
    cap_text = getCapitalisedText(tokenised_tweet)
    if FEATURE_SA_CAPS_PRESENCE in features:  # NOT in use
        features_dict[FEATURE_SA_CAPS_PRESENCE] = getCapitalisedTextPresence(cap_text)
        
    if FEATURE_SA_CAPS_POLARITY in features:  # in use
        features_dict[FEATURE_SA_CAPS_POLARITY] = getCapitalisedTextPolarityCount(
                                                     cap_text,
                                                     tweet_polarity_info[POLARITY_WORD])
    
    if FEATURE_SA_CAPS_PERCENTAGE in features:  # in use
        features_dict[FEATURE_SA_CAPS_PERCENTAGE] = getCapitalisedTextPercentage(cap_text, tokenised_tweet)
#         features_dict[FEATURE_SA_CAPS_PERCENTAGE] = getCapitalisedTextPercentage(cap_text, json_data['text'])
    # Cannot union
    
        
    # === Unigrams === #
    if FEATURE_TEXT in features:  # in use
        features_dict[FEATURE_TEXT] = getText(tokenised_tweet, negation_flags,
                                              use_negation=False)
        
    if FEATURE_HASHTAG in features:  # in use
        features_dict[FEATURE_HASHTAG] = getHashTags_SA(json_data, tokenised_tweet_no_filter)
    
    # === User === #
    if FEATURE_USER in features:  # NOT in use
        features_dict[FEATURE_USER] = {FEATURE_VALUE:{json_data['id_str']: 1 }}
    
    if FEATURE_USER_MENTIONS in features:  # NOT in use
        features_dict[FEATURE_USER_MENTIONS] = getUserMentions_SA(json_data, tokenised_tweet_no_filter)
        
    # === Emoticons === #
    if FEATURE_SA_EMOTICONS in features:  # in use
        features_dict[FEATURE_SA_EMOTICONS] = getEmoticons(tokenised_tweet, emo_dict)
        
    if FEATURE_SA_EMOTICONS_POLARITY in features:  # in use
        features_dict[FEATURE_SA_EMOTICONS_POLARITY] = getEmoticonPolarityCount(tokenised_tweet, emo_dict)
    
    # === Exclamation === #
    if FEATURE_SA_EXCLAMATION_PRESENCE in features:  # in use
        features_dict[FEATURE_SA_EXCLAMATION_PRESENCE] = getExclamationPrescence(tokenised_tweet)
        
    if FEATURE_SA_EXCLAMATION_COUNT in features:  # NOT in use
        features_dict[FEATURE_SA_EXCLAMATION_COUNT] = getExclamationCount(tokenised_tweet)
    
    # === Twitter Token === #    
    if FEATURE_SA_TWITTER_TOKEN_COUNT in features:  # NOT in use
        twitter_tokens = getTwitterTokenCount(json_data, tokenised_tweet_no_filter)
        features_dict[FEATURE_SA_TWITTER_TOKEN_COUNT] = getTwitterTokenPercentage(twitter_tokens, json_data['text'])
#         {FEATURE_VALUE: {"TWITTER_TOKEN_COUNT": twitter_token_count[FEATURE_COUNT]}}


#     print json_data['text']
#     print features_dict
    
    return {TWEET_FULL: json_data['text'], TWEET_FEATURES: features_dict}

def getKeyInfoForSA(data_filename, categories_list, groundtruth_list, features_used):
    '''
    Params:
        data_filename: input data file in json format
        categories_list: [cat1, cat2, cat3]
        groundtruth_list: [{CATEGORY: category, POLARITY: polarity, TWEET_ID: tweetid}]
        features: features list, defaults to FEATURES_SA_DEFAULT
        
    Returns:
    {
        'category' : {
            CLASS_SVM_POSITIVE:{
                PROCESSED_TWEETS : [{
                    TWEET_FULL: This was a triumph, 
                    TWEET_FEATURES: {
                        FEATURE_TEXT: {FEATURE_COUNT: number, FEATURE_VALUE: {feature: count}} , 
                    }
                    
                }],
                FEATURES: {
                    FEATURE_TEXT: { feature: df } ...
                }
            },
            
            CLASS_SVM_NEGATIVE:{
                PROCESSED_TWEETS : [{
                    TWEET_FULL: This was a triumph, 
                    TWEET_FEATURES: {
                        FEATURE_TEXT: {FEATURE_COUNT: number, FEATURE_VALUE: {feature: count}} , 
                    }
                    
                }],
                FEATURES: {
                    FEATURE_TEXT: { feature: df } ...
                }
            },
            
            CLASS_SVM_NEUTRAL:{
                PROCESSED_TWEETS : [{
                    TWEET_FULL: This was a triumph, 
                    TWEET_FEATURES: {
                        FEATURE_TEXT: {FEATURE_COUNT: number, FEATURE_VALUE: {feature: count}} , 
                    }
                    
                }],
                FEATURES: {
                    FEATURE_TEXT: { feature: df } ...
                }
            },
            
            UNIQUE_FEATURES: {
                FEATURE_TEXT: { feature: df } , ... 
            }
        }
    }
    '''
    returnmap = {}
    
    # Initialize category dictionaries
    categories_list.append(NO_CATEGORY)
    for category in categories_list:
        returnmap[category] = {}
        returnmap[category][CLASS_SVM_POSITIVE] = {}
        returnmap[category][CLASS_SVM_POSITIVE][PROCESSED_TWEETS] = []
        
        returnmap[category][CLASS_SVM_NEGATIVE] = {}
        returnmap[category][CLASS_SVM_NEGATIVE][PROCESSED_TWEETS] = []
        
        returnmap[category][CLASS_SVM_NEUTRAL] = {}
        returnmap[category][CLASS_SVM_NEUTRAL][PROCESSED_TWEETS] = []
    
    with codecs.open(data_filename, encoding='cp1252') as k:
        debugPrint(">> extracting features from tweet")
        for idx, line in enumerate(k):
            # extract all features from tweet
            json_data = json.loads(line, encoding='cp1252')
            tweet_keyinfo = extractSentiFeaturesFromTweet(json_data, features_used)
#             print tweet_keyinfo

            # Classify into sentiment positive/negative/neutral
            gt_item = groundtruth_list[idx]
            if gt_item[POLARITY] == POLARITY_POSITIVE:
                returnmap[NO_CATEGORY][CLASS_SVM_POSITIVE][PROCESSED_TWEETS].append(tweet_keyinfo)
                returnmap[gt_item[CATEGORY]][CLASS_SVM_POSITIVE][PROCESSED_TWEETS].append(tweet_keyinfo)
            
            elif gt_item[POLARITY] == POLARITY_NEGATIVE:
                returnmap[NO_CATEGORY][CLASS_SVM_NEGATIVE][PROCESSED_TWEETS].append(tweet_keyinfo)
                returnmap[gt_item[CATEGORY]][CLASS_SVM_NEGATIVE][PROCESSED_TWEETS].append(tweet_keyinfo)
            
            elif gt_item[POLARITY] == POLARITY_NEUTRAL:
                returnmap[NO_CATEGORY][CLASS_SVM_NEUTRAL][PROCESSED_TWEETS].append(tweet_keyinfo)
                returnmap[gt_item[CATEGORY]][CLASS_SVM_NEUTRAL][PROCESSED_TWEETS].append(tweet_keyinfo)
        
        # collate unique features
        debugPrint(">> collating unique features...")
        for category in categories_list:
            debugPrint(">> collating for %s" % category)
#             unique_features_dict = initializeFeatureDict(features)
            unique_features_dict = {}
            for feature in features_used:
                # TODO: whitelist 
                if feature == FEATURE_SA_REPLIES or feature == FEATURE_SA_TEMPORAL:
                    continue
                unique_features_dict[feature] = {}
                
            pos_unique_features = getUniqueFeaturesForClass(
                                    returnmap[category][CLASS_SVM_POSITIVE][PROCESSED_TWEETS],
                                    unique_features_dict, features_used)
            returnmap[category][CLASS_SVM_POSITIVE][FEATURES] = pos_unique_features
            
            neg_unique_features = getUniqueFeaturesForClass(
                                   returnmap[category][CLASS_SVM_NEGATIVE][PROCESSED_TWEETS],
                                   unique_features_dict, features_used)
            returnmap[category][CLASS_SVM_NEGATIVE][FEATURES] = neg_unique_features
            
            neut_unique_features = getUniqueFeaturesForClass(
                                    returnmap[category][CLASS_SVM_NEUTRAL][PROCESSED_TWEETS],
                                    unique_features_dict, features_used)
            returnmap[category][CLASS_SVM_NEUTRAL][FEATURES] = neut_unique_features
            
            # resolve global unique features
            returnmap[category][UNIQUE_FEATURES] = unique_features_dict
        
    return returnmap

def getUniqueFeaturesForClass(processed_tweets_list, categorywide_unique_features, features_used=FEATURES_SA_DEFAULT):
    '''
    Params:
        processed_tweets_list: [] of tweets of class
        categorywide_unique_features: {} to keep track of unique features of a category e.g. apple, google,...
        features_used: [] of features in use from CS4242_Assg2.constants
    Return:
        class_unique_features: { FEATURE_TYPE_... : {feature: value}}
    '''
    class_unique_features = {}
    for feature in features_used:
        # TODO: whitelist
        if feature == FEATURE_SA_REPLIES or feature == FEATURE_SA_TEMPORAL:
            continue
        class_unique_features[feature] = {}
                
    for processed_tweet in processed_tweets_list:
        for feature in features_used:
            # TODO: whitelist
            if feature == FEATURE_SA_REPLIES or feature == FEATURE_SA_TEMPORAL:
                continue
        
            val_dict = processed_tweet[TWEET_FEATURES][feature][FEATURE_VALUE]
            for key, val in val_dict.iteritems():
                addToCountDict(categorywide_unique_features[feature], key, 1)
                addToCountDict(class_unique_features[feature], key, 1)         
    return class_unique_features

def initializeFeatureDict(features=FEATURES_SA_DEFAULT):
    '''
    Quick initialization of feature dictionary
    '''
    dict1 = {}
    for feature in features:
        dict[feature] = {}
    return dict1

if __name__ == '__main__':
    gen = parseLabelFile(PATH_GROUNDTRUTH_TRAINING)
    categories_list = gen['categories']
    categories_list.append('no_category')
    groundtruth_list = gen['groundtruth_list']
    getKeyInfoForSA(PATH_TRAINING_DATA, categories_list, groundtruth_list, FEATURES_SA_DEFAULT)  # A test for unicode errors
    pass 
