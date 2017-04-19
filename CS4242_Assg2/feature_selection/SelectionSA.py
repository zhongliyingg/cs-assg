'''
Created on Mar 13, 2014

@author: LIYING
'''
import operator

from CS4242_Assg2.constants import *
from console_debug.debug_methods import writeDebugListToFile


def selectTweetsForSA(tweet_sample, size, tweet_sample_polarity):
    selected_tweets = []
    if size > len(tweet_sample):
        size = len(tweet_sample)
    
    tweet_polarity_count = []
    for tweet in tweet_sample:
#         if len(selected_tweets) == size:
#             break
        tweet_word_polarity = tweet[TWEET_FEATURES][FEATURE_SA_POLARITY_TEXT][FEATURE_VALUE]
#         print tweet_word_polarity
        other_polarity_count = 0
        if tweet_sample_polarity == POLARITY_POSITIVE:
            if 'POLARITY_TEXT_NEG' in tweet_word_polarity:
                other_polarity_count += tweet_word_polarity['POLARITY_TEXT_NEG']
            if 'POLARITY_TEXT_NEU' in tweet_word_polarity:
                other_polarity_count += tweet_word_polarity['POLARITY_TEXT_NEU']  
        
        elif tweet_sample_polarity == POLARITY_NEGATIVE:
            if 'POLARITY_TEXT_POS' in tweet_word_polarity:
                other_polarity_count += tweet_word_polarity['POLARITY_TEXT_POS']
            if 'POLARITY_TEXT_NEU' in tweet_word_polarity:
                other_polarity_count += tweet_word_polarity['POLARITY_TEXT_NEU']
                
        elif tweet_sample_polarity == POLARITY_NEUTRAL:
            if 'POLARITY_TEXT_POS' in tweet_word_polarity:
                other_polarity_count += tweet_word_polarity['POLARITY_TEXT_POS']
            if 'POLARITY_TEXT_NEG' in tweet_word_polarity:
                other_polarity_count += tweet_word_polarity['POLARITY_TEXT_NEG']
                
        tweet_polarity_count.append((tweet, other_polarity_count))
#         print polarity, other_polarity_count 
#         for word in tweet_word_polarity:
#             if tweet_word_polarity[word] == POLARITY_NONE:
#                 continue
#             if tweet_word_polarity[word] != polarity:
#                 selected_tweets.append(tweet)
#                 break

    tweet_polarity_count = sorted(tweet_polarity_count, key=lambda x: x[1], reverse=True)
#     print tweet_polarity_count
#     writeDebugListToFile("sorted_tweet_polarity_count.txt", tweet_polarity_count)
    for tweet, polarity_count in tweet_polarity_count:
        if len(selected_tweets) == size:
            break
        selected_tweets.append(tweet)
        
    return selected_tweets