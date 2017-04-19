# -*- coding: cp1252 -*-
'''
Created on Feb 23, 2014

@author: simkerncheh
'''
import codecs
import json
import re
import string
import unicodedata

from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer

from CS4242_Assg2.constants import *
from console_debug.debug_methods import *
from parser2.Normalizer import Normalizer
from parser2.ParserCommon import parseLabelFile, addToCountDict, \
    filterIrrelevantTokens, removePunctuationsAndNumbers


stemmer = LancasterStemmer()
normalizer = Normalizer()

def getKeyInfoForClassifier(filename, categories_list, groundtruth_list, features=FEATURES_DEFAULT):
    '''
    Extracts all features from input files.
    
    Params:
        filename: input DATA file
        categories_list: list of categories, e.g ['Apple', 'Google', 'Twitter']
        groundtruth_list: list of groundtruths, e.g [{CATEGORY: category, POLARITY: polarity, TWEET_ID: tweetid}]
        features (optional):     [FEATURE_TEXT, FEATURE_HASHTAG, FEATURE_GEOINFO, FEATURE_FOLLOWED_CATEGORIES,
                                FEATURE_USER, FEATURE_USER_MENTIONS]
    
    Returns: 
        {
            'category' : {
                POSITIVE:{
                    PROCESSED_TWEETS : [{
                        TWEET_FULL: This was a triumph, 
                        TWEET_FEATURES: {
                            FEATURE_TEXT: {} , 
                            FEATURE_GEOLOCATION : str
                        }
                        
                    }],
                    FEATURES: {
                        FEATURE_TEXT: {} ...
                    }
                },
                
                NEGATIVE:{
                    PROCESSED_TWEETS : [{
                        TWEET_FULL: This was a triumph, 
                        TWEET_FEATURES: {
                            FEATURE_TEXT: {} , 
                            FEATURE_GEOLOCATION : str
                        }
                        
                    }],
                    FEATURES: {
                        FEATURE_TEXT: {} ...
                        FEATURE_HASHTAG: []
                    }
                },
                
                UNIQUE_FEATURES: {
                    FEATURE_TEXT: {} , ... 
                }
            }
        }
    '''
    
    returnmap = {}
    
    for category in categories_list:
        # category wide variables
        processed_tweets_list = []
        unique_features_map = {}
        
        positive_processed_tweet_list = []
        negative_processed_tweet_list = []
        
        positive_features_map = {}
        negative_features_map = {}
        
        # Initialize unique feature maps within category
        for feature in features:
            if feature == FEATURE_TEXT:
                feature_text_unique = {}
                pos_feature_text_unique = {}
                neg_feature_text_unique = {}
                
            elif feature == FEATURE_HASHTAG:
                feature_hashtag_unique = {}
                pos_feature_hashtag_unique = {}
                neg_feature_hashtag_unique = {}
                
            elif feature == FEATURE_GEOINFO:
                feature_geoinfo_unique = {}
                pos_feature_geoinfo_unique = {}
                neg_feature_geoinfo_unique = {}
                
            elif feature == FEATURE_FOLLOWED_CATEGORIES:
                feature_followed_cat_unique = {}
                pos_feature_followed_cat_unique = {}
                neg_feature_followed_cat_unique = {}
                
            elif feature == FEATURE_USER:
                feature_user_unique = {}
                pos_feature_user_unique = {}
                neg_feature_user_unique = {}
                
            elif feature == FEATURE_USER_MENTIONS:
                feature_usermentions_unique = {}
                pos_feature_usermentions_unique = {}
                neg_feature_usermentions_unique = {}
            
            elif feature == FEATURE_CATEGORY:
                feature_category_unique = {}
                pos_feature_category_unique = {}
                neg_feature_category_unique = {}
                

        # Extract & Process Features
        with codecs.open(filename, encoding='cp1252') as k:
            for index, line in enumerate(k):
                json_data = json.loads(line, encoding='cp1252')
                tweet_keyinfo = extractFeaturesFromTweet(json_data, categories_list, features, category)
                
                if groundtruth_list[index][CATEGORY] == category:
                    positive_processed_tweet_list.append(tweet_keyinfo)
                else:
                    negative_processed_tweet_list.append(tweet_keyinfo)
                
                processed_tweets_list.append(tweet_keyinfo)
            
        # check unique tweet_keyinfo across positive, negative and all
        for tweet_keyinfo in positive_processed_tweet_list:
            for feature in features:
                if feature == FEATURE_TEXT:
                    text_count_dict = tweet_keyinfo[TWEET_FEATURES][FEATURE_TEXT]
                    for key, count in text_count_dict.iteritems():
                        addToCountDict(pos_feature_text_unique, key, 1)
                        
                elif feature == FEATURE_HASHTAG:
                    for hashtag in tweet_keyinfo[TWEET_FEATURES][FEATURE_HASHTAG]:
                        addToCountDict(pos_feature_hashtag_unique, hashtag, 1)
                        
                elif feature == FEATURE_GEOINFO:
                    if tweet_keyinfo[TWEET_FEATURES][FEATURE_GEOINFO] != '':
                        addToCountDict(pos_feature_geoinfo_unique, tweet_keyinfo[TWEET_FEATURES][FEATURE_GEOINFO], 1)
                    
                elif feature == FEATURE_FOLLOWED_CATEGORIES:
                    # TODO: Consider implementing
                    pass
                
                elif feature == FEATURE_USER:
                    addToCountDict(pos_feature_user_unique, tweet_keyinfo[TWEET_FEATURES][FEATURE_USER], 1)
                    
                elif feature == FEATURE_USER_MENTIONS:
                    for usermention in tweet_keyinfo[TWEET_FEATURES][FEATURE_USER_MENTIONS]:
                        addToCountDict(pos_feature_usermentions_unique, usermention, 1)
                
                elif feature == FEATURE_CATEGORY:
                    for item in tweet_keyinfo[TWEET_FEATURES][FEATURE_CATEGORY]:
                        addToCountDict(pos_feature_category_unique, item , 1)
        
        # debug files will be written only if settings.DEBUG_CODE = True
#         writeDebugCountDictToFile("%s_pos_feature_text_unique.txt" % category, pos_feature_text_unique)
#         writeDebugCountDictToFile("%s_pos_feature_hashtag_unique.txt" % category, pos_feature_hashtag_unique)
#         writeDebugCountDictToFile("%s_pos_feature_geoinfo_unique.txt" % category, pos_feature_geoinfo_unique)
#         writeDebugCountDictToFile("%s_pos_feature_user_unique.txt" % category, pos_feature_user_unique)
#         writeDebugCountDictToFile("%s_pos_feature_usermentions_unique.txt" % category, pos_feature_usermentions_unique)
                        
        for tweet_keyinfo in negative_processed_tweet_list:
            for feature in features:
                if feature == FEATURE_TEXT:
                    text_count_dict = tweet_keyinfo[TWEET_FEATURES][FEATURE_TEXT]
                    for key, count in text_count_dict.iteritems():
                        addToCountDict(neg_feature_text_unique, key, 1)
                elif feature == FEATURE_HASHTAG:
                    for hashtag in tweet_keyinfo[TWEET_FEATURES][FEATURE_HASHTAG]:
                        addToCountDict(neg_feature_hashtag_unique, hashtag, 1)
                elif feature == FEATURE_GEOINFO:
                    addToCountDict(neg_feature_geoinfo_unique, tweet_keyinfo[TWEET_FEATURES][FEATURE_GEOINFO], 1)
                elif feature == FEATURE_FOLLOWED_CATEGORIES:
                    # TODO: Consider implementing
                    pass
                elif feature == FEATURE_USER:
                    addToCountDict(neg_feature_user_unique, tweet_keyinfo[TWEET_FEATURES][FEATURE_USER], 1)
                    
                elif feature == FEATURE_USER_MENTIONS:
                    for usermention in tweet_keyinfo[TWEET_FEATURES][FEATURE_USER_MENTIONS]:
                        addToCountDict(neg_feature_usermentions_unique, usermention, 1)
                        
                elif feature == FEATURE_CATEGORY:
                    for item in tweet_keyinfo[TWEET_FEATURES][FEATURE_CATEGORY]:
                        addToCountDict(neg_feature_category_unique, item , 1)
            
        
        for tweet_keyinfo in processed_tweets_list:
            for feature in features:
                if feature == FEATURE_TEXT:
                    text_count_dict = tweet_keyinfo[TWEET_FEATURES][FEATURE_TEXT]
                    for key, count in text_count_dict.iteritems():
                        addToCountDict(feature_text_unique, key, 1)
                        
                elif feature == FEATURE_HASHTAG:
                    for hashtag in tweet_keyinfo[TWEET_FEATURES][FEATURE_HASHTAG]:
                        addToCountDict(feature_hashtag_unique, hashtag, 1)
                elif feature == FEATURE_GEOINFO:
                    addToCountDict(feature_geoinfo_unique, tweet_keyinfo[TWEET_FEATURES][FEATURE_GEOINFO], 1)
                elif feature == FEATURE_FOLLOWED_CATEGORIES:
                    # TODO: Consider implementing
                    pass
                elif feature == FEATURE_USER:
                    addToCountDict(feature_user_unique, tweet_keyinfo[TWEET_FEATURES][FEATURE_USER], 1)
                elif feature == FEATURE_USER_MENTIONS:
                    for usermention in tweet_keyinfo[TWEET_FEATURES][FEATURE_USER_MENTIONS]:
                        addToCountDict(feature_usermentions_unique, usermention, 1)
                        
                elif feature == FEATURE_CATEGORY:
                    for item in tweet_keyinfo[TWEET_FEATURES][FEATURE_CATEGORY]:
                        addToCountDict(feature_category_unique, item , 1)
                        
        for feature in features:
            if feature == FEATURE_TEXT:
                unique_features_map[FEATURE_TEXT] = feature_text_unique
                positive_features_map[FEATURE_TEXT] = pos_feature_text_unique
                negative_features_map[FEATURE_TEXT] = neg_feature_text_unique
            elif feature == FEATURE_HASHTAG:
                unique_features_map[FEATURE_HASHTAG] = feature_hashtag_unique
                positive_features_map[FEATURE_HASHTAG] = pos_feature_hashtag_unique
                negative_features_map[FEATURE_HASHTAG] = neg_feature_hashtag_unique
            elif feature == FEATURE_GEOINFO:
                unique_features_map[FEATURE_GEOINFO] = feature_geoinfo_unique
                positive_features_map[FEATURE_GEOINFO] = pos_feature_geoinfo_unique
                negative_features_map[FEATURE_GEOINFO] = neg_feature_geoinfo_unique
            elif feature == FEATURE_FOLLOWED_CATEGORIES:
                unique_features_map[FEATURE_FOLLOWED_CATEGORIES] = feature_followed_cat_unique
                positive_features_map[FEATURE_FOLLOWED_CATEGORIES] = pos_feature_followed_cat_unique
                negative_features_map[FEATURE_FOLLOWED_CATEGORIES] = neg_feature_followed_cat_unique
            elif feature == FEATURE_USER:
                unique_features_map[FEATURE_USER] = feature_user_unique
                positive_features_map[FEATURE_USER] = pos_feature_user_unique
                negative_features_map[FEATURE_USER] = neg_feature_user_unique
            elif feature == FEATURE_USER_MENTIONS:
                unique_features_map[FEATURE_USER_MENTIONS] = feature_usermentions_unique
                positive_features_map[FEATURE_USER_MENTIONS] = pos_feature_usermentions_unique
                negative_features_map[FEATURE_USER_MENTIONS] = neg_feature_usermentions_unique
            elif feature == FEATURE_CATEGORY:
                unique_features_map[FEATURE_CATEGORY] = feature_category_unique
                positive_features_map[FEATURE_CATEGORY] = pos_feature_category_unique
                negative_features_map[FEATURE_CATEGORY] = neg_feature_category_unique
            
        returnmap[category] = {}        
        returnmap[category][POSITIVE] = { PROCESSED_TWEETS: positive_processed_tweet_list, FEATURES: positive_features_map }
        returnmap[category][NEGATIVE] = { PROCESSED_TWEETS: negative_processed_tweet_list, FEATURES: negative_features_map }
        returnmap[category][UNIQUE_FEATURES] = unique_features_map
          
    return returnmap



def extractFeaturesFromTweet(json_data, categorieslist, features=FEATURES_DEFAULT, currentcategory=None,):
    '''
    Processes one line of tweet from the input file
    Extracts relevant features defined in 'features' parameter
    
    Returns:
    {TWEET_FULL: This was a triumph, TWEET_FEATURES: {FEATURE_TEXT: __ , 'geolocation' : __ }}
    '''
    
    features_dict = {}
    
    for feature in features:
        if feature == FEATURE_TEXT:
            # {'word' : occurrence }
            features_dict[FEATURE_TEXT] = extractTextFeatures(json_data)
            if FEATURE_CATEGORY in features:
                features_dict[FEATURE_CATEGORY] = []
                if currentcategory == None:
                    for category in categorieslist:
                        if stemmer.stem(category) in features_dict[FEATURE_TEXT]:
                            features_dict[FEATURE_CATEGORY].append('CAT_%s' % (category))
                else:
                    if stemmer.stem(currentcategory) in features_dict[FEATURE_TEXT]:
                        features_dict[FEATURE_CATEGORY].append('CAT_%s' % (currentcategory))
                        
                        
        elif feature == FEATURE_HASHTAG:
            features_dict[FEATURE_HASHTAG] = getHashTags(json_data)
            if FEATURE_CATEGORY in features:
                if currentcategory == None:
                    for category in categorieslist:
                        ht_concat_catname = "#HT_%s" % (category)
                        if ht_concat_catname in features_dict[FEATURE_HASHTAG]:
                            features_dict[FEATURE_CATEGORY].append('CAT_%s' % (category))
                            
                else:
                    ht_concat_catname = "#HT_%s" % (currentcategory)
                    if ht_concat_catname in features_dict[FEATURE_TEXT]:
                        features_dict[FEATURE_CATEGORY].append('CAT_%s' % (currentcategory))
                        
                        
            
        elif feature == FEATURE_GEOINFO:
            features_dict[FEATURE_GEOINFO] = getGeoInfo(json_data)
        elif feature == FEATURE_USER_MENTIONS:
            features_dict[FEATURE_USER_MENTIONS] = getUserMentions(json_data)
        elif feature == FEATURE_USER:
            features_dict[FEATURE_USER] = json_data['user']['id']
       
            
        features_dict[FEATURE_CREATED_AT] = json_data['created_at']
            
    return {TWEET_FULL: json_data['text'], TWEET_FEATURES: features_dict}                     

def extractTextFeatures(json_data):
    
    tweet_words = {}
    
    # Remove unnecessary tokens
    tweet_text = filterIrrelevantTokens(json_data)
    
    unicode_normalized_tweet = unicodedata.normalize('NFKD', tweet_text).encode('ascii', 'ignore').lower()
    tweet_wordlist = normalizer.normalizeTweet(unicode_normalized_tweet)
    # tweet wordlist = ['word', 'word2'] etc
    
    for word in tweet_wordlist:
        stripped_punct_num_word = removePunctuationsAndNumbers(word)
        for w in stripped_punct_num_word:
            if w not in stopwords.words('english'):
                w2 = stemmer.stem(w) 
                addToCountDict(tweet_words, w2, 1) 
    return tweet_words
    
def getGeoInfo(json_data):
    '''
    Retrieves Geographical information pertaining to user location
    
    Return: 
        timezone information if available, 
        empty string if not available
    '''
    
    if 'time_zone' in json_data['user' ] \
    and json_data['user']['time_zone'] is not None \
    and json_data['user']['time_zone'] != '':
        user_timezone = "GEO-TZ_" + json_data['user']['time_zone']
    else:
        user_timezone = ''
        
    return user_timezone

def getHashTags(json_data):
    hashtags = []
    for ht in json_data['entities']['hashtags']:
        hashtags.append("#HT_" + ht['text'])
    return hashtags
    
def getUserMentions(json_data):
    '''
    Get user ids of users mentioned in tweet, include tweeter of tweet
    '''
    user_mentions = []
    for um in json_data['entities']['user_mentions']:
        user_mentions.append("@UM_" + um['id_str'])
    user_mentions.append("@UM_" + str(json_data['user']['id']))
    return user_mentions
            
if __name__ == '__main__':
    gen = parseLabelFile(PATH_GROUNDTRUTH_TRAINING)
    categories_list = gen['categories']
    groundtruth_list = gen['groundtruth_list']
    getKeyInfoForClassifier(PATH_TRAINING_DATA, categories_list, groundtruth_list)  # A test for unicode errors
    pass    

