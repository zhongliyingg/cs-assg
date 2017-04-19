'''
Created on Mar 6, 2014

@author: LIYING
'''
import codecs
import re
import string

from CS4242_Assg2.constants import *
from console_debug.debug_methods import debugPrint
from web.models import SVMStatesClassifier


regex_RT = re.compile(r'\bRT\b')
regex_punctuation_html_plus = re.compile('^(&#39;|&quot;|&gt;|&lt;|&amp;)+$') 
regex_punctuation_digit2_plus = re.compile('^[%s\d]+$' % re.escape(string.punctuation))
regex_punctuation_plus = re.compile('^[%s]+$' % re.escape(string.punctuation))

regex_punctuation_html = re.compile('&#39;|&quot;|&gt;|&lt;|&amp;') 
regex_punctuation_digit2 = re.compile('[%s\d]' % re.escape(string.punctuation))
regex_punctuation_digit = re.compile('([%s\d]|&#39;|&quot;|&gt;|&lt;|&amp;)+' % re.escape(string.punctuation))

regex_only_punctuation_digit = re.compile('^[%s\d]+|(&#39;|&quot;|&gt;|&lt;|&amp;)+$' % re.escape(string.punctuation))
regex_trailing_punctuation_digit = re.compile('[%s\d]+$' % re.escape(string.punctuation))

def addToCountDict(dictionary, key, inc):
    if key in dictionary:
        dictionary[key] = dictionary[key] + inc
    else:
        dictionary[key] = inc
    return dictionary

def filterIrrelevantTokens(json_tweet, filter_hashtags=True, filter_user_mentions=True):
    '''
    Filter irrelevant tokens from tweet, including user_mentions, hashtags and urls 
    
    Params: 
        json_tweet: full tweet data
    Return:
        filteredTweet: filtered tweet string
    '''
    
    stripIndex = []
    for key, entity in json_tweet['entities'].iteritems():
        if key == 'hashtags' and not filter_hashtags:
            continue
        elif key == 'user_mentions' and not filter_user_mentions:
            continue
        for item in entity:
            stripIndex.append(item['indices'])
    stripIndex.sort(cmp=None, key=lambda x: int(x[0]), reverse=True)       
    
    # strip unwanted info
    filteredTweet = json_tweet['text']
    for idx in stripIndex:
        right = filteredTweet[int(idx[1]):]
        left = filteredTweet[:int(idx[0])]
        filteredTweet = left + right
    
    # remove RT
    filteredTweet = re.sub(regex_RT, '', filteredTweet, re.IGNORECASE)
    
    return filteredTweet

def removePunctuationsAndNumbers(word):
    '''
    Remove punctuations and numbers from word
    Params:
        word: target word
    Output:
        stripped_words: [] of words split by punctuations/numbers
    ''' 
    stripped_words = []
    w_removeHtmlTag = re.split(regex_punctuation_html, word)
    if re.search(regex_punctuation_digit2, word) or re.search(regex_punctuation_html, word):
#     if re.match(regex_punctuation_digit2, word) or re.match(regex_punctuation_html, word):
        for w in w_removeHtmlTag:
            if w != '':
                w_removePunctNum = re.split(regex_punctuation_digit2, w)
                for w2 in w_removePunctNum:
                    if w2 != '' and len(w2) > 2:
                        stripped_words.append(w2)
    else:
        stripped_words.append(word)
#     print word, stripped_words    
    return stripped_words

def parseLabelFile(labelfilename):
    '''
    Returns:
         {
             'categories': ['abc', 'def'], 
             'groundtruth_list': [CATEGORY: 'abc', POLARITY: 'positive', TWEET_ID: "123" <- str ]
             'categories_map' : {
                 categoryname: {
                     CLASS_SVM_POSITIVE: [tweetid, tweetid]
                     ...
                 }
             }
         }
    '''
    categories = []
    groundtruth_list = []
    with codecs.open(labelfilename, encoding='cp1252') as f:
        for line in f:
            splitarray = line.strip().split(',')
            
            category = splitarray[0][1:-1]
            polarity = splitarray[1][1:-1]
            tweetid = splitarray[2][1:-1]
            
            if category not in categories:
                categories.append(category)
            
            
            groundtruth_list.append({CATEGORY: category, POLARITY: polarity, TWEET_ID: tweetid})
    
    return {'categories': categories, 'groundtruth_list': groundtruth_list}

def splitfilebycategory(filename, combined_results):
    '''
    Inputs:
        filename: file to split
        combined_results: output from performClassification in Jobs_Classifier
        
            {
                'apple': [0,0,1,0...],
                'twitter': [0,0,0,...],
            }
    Returns:
        {
            'apple': [json_tweet, json_tweet],
            ...
        }
    '''
    returnresult = {}
    svmstates = SVMStatesClassifier.objects.all()
    categorieslist = []
    returnresult[NO_CATEGORY] = []
    
    for svm in svmstates:
        categorieslist.append(svm.classifier_name)
        returnresult[svm.classifier_name] = []
        
    with codecs.open(filename, encoding='cp1252') as f:
        for idx, line in enumerate(f):
            for category in categorieslist:
                if combined_results[category][idx] == POSITIVE:
                    returnresult[category].append(line)
            returnresult[NO_CATEGORY].append(line)
    
    for cat, val in returnresult.iteritems():
        debugPrint(cat, len(val))
    return returnresult
