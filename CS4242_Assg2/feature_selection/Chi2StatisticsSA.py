'''
Created on Mar 14, 2014

@author: LIYING
'''
from CS4242_Assg2.constants import *
from parser2.ParserCommon import addToCountDict


def calculateChi2ValuesSA(unique_feat, feature_set, sample_size_set):
    '''
        Calculate Chi2 values of all unique features using lecture's formula
         
        Params:
            unique_feat: [feat] of unique features
            feature_set: {senti_type: features} of features from each sentiment
            sample_size_set: {senti_type:sample_tweet_count} of each sentiment
        Returns:
            chi2_val_list: {senti_type: {feat: chi2_val}}of calculated chi2 values
    '''
     
#     print 'using calculateChi2Values...'
    sentiment_feature_set = {}
    for target_sentiment in feature_set.iterkeys():
        target_senti_feat_dict = feature_set[target_sentiment]
        target_senti_sample_size = sample_size_set[target_sentiment]
        
        # merge the other sentiment feature dictionaries
        other_senti_feat_dict = {}
        other_senti_sample_size = 0
        for sentiment in feature_set.iterkeys():
            if sentiment != target_sentiment:
                for item, value in feature_set[sentiment].iteritems():
                    addToCountDict(other_senti_feat_dict, item, value) 
                other_senti_sample_size += sample_size_set[sentiment]
        
        target_sent_feat_set = {}        
        target_sent_feat_set['target_feat_dict'] = target_senti_feat_dict
        target_sent_feat_set['target_sample_size'] = sum(target_senti_feat_dict.itervalues())
        target_sent_feat_set['other_feat_dict'] = other_senti_feat_dict
        target_sent_feat_set['other_sample_size'] = sum(other_senti_feat_dict.itervalues())
        sentiment_feature_set[target_sentiment] = target_sent_feat_set

    
#         target_senti_sample_size = sum(target_senti_feat_dict.itervalues())
#         other_senti_sample_size = sum(other_senti_feat_dict.itervalues())
#         print target_sent_feat_set['target_sample_size'], target_sent_feat_set['other_sample_size']
#         print sum(unique_feat.itervalues())
    chi2_val_dict = {}                
    for target_sentiment in feature_set.iterkeys():
        target_sent_feat_set = sentiment_feature_set[target_sentiment] 
        target_senti_feat_dict = target_sent_feat_set['target_feat_dict'] 
        target_senti_sample_size = target_sent_feat_set['target_sample_size'] 
        
        other_senti_feat_dict = target_sent_feat_set['other_feat_dict'] 
        other_senti_sample_size = target_sent_feat_set['other_sample_size'] 
            
        chi2_word_val = {}  
        for f in target_senti_feat_dict.iterkeys():
            # calculate chi2
            A = 0 # num of tweets in target cat that contains feature
            B = 0 # num of tweets not in target cat that contains feature
            C = 0 # num of tweets in target cat that doesnt contains feature
            D = 0 # num of tweets not in target cat that doesnt contains feature
            
            if f in target_senti_feat_dict:
                A = target_senti_feat_dict[f] 
            if f in other_senti_feat_dict:
                B = other_senti_feat_dict[f]
            

            C = target_senti_sample_size - A 
            D = other_senti_sample_size - B 
               
            chi2_word_val[f] = calculateChi2(A, B, C, D)
#             print f,A,B,C,D, chi2_word_val[f]
#             break
            
        chi2_val_dict[target_sentiment] = chi2_word_val
    return chi2_val_dict

def calculateChi2(A, B, C, D):
    chi2_val_num = (A+B+C+D)*(A*D - C*B)*(A*D - C*B)
    chi2_val_denom = (A+C)*(B+D)*(A+B)*(C+D)
     
    if chi2_val_denom == 0:
        chi2_val = 0
    else:
        chi2_val = float(chi2_val_num)/float(chi2_val_denom)
    return chi2_val