'''
Created on Feb 27, 2014

@author: LIYING
'''
import math
import operator

from feature_selection.Chi2Statistics import calculateChi2Values
from CS4242_Assg2.constants import TWEET_FEATURES


def selectFeatureByChi2(unique_feat, pos_feat, neg_feat, pos_sample_size, neg_sample_size, num_of_feat):
    '''
    Select features by Chi2 values
    
    Params:
        unique_feat: [] of unqiue features
        pos_feat: {word: count} of positive features
        neg_feat: {word: count} of negative features
        pos_sample_size: number of positive samples
        neg_sample_size: number of negative samples
        num_of_feat: number features to select
    Returns:
        List of tuples (features, chi2 value)
    '''
#     feat_chi2_val = calculateChi2Values_sklearn(key_info)
    feat_chi2_val = calculateChi2Values(unique_feat, pos_feat, neg_feat, pos_sample_size, neg_sample_size)
    
    pos_chi2_val = {}
    for feature in pos_feat.iterkeys():
        if feature in feat_chi2_val:
            pos_chi2_val[feature] = feat_chi2_val[feature]
    
    if num_of_feat > len(pos_feat):
        num_of_feat = len(pos_feat)
    top_k_features = selectTopKFeatures(pos_chi2_val, num_of_feat)

#     top_k_features = SelectTopKChi2Features(pos_chi2_val, top_k)
    
    return top_k_features

def selectTopKFeatures(feat_val_dict, top_k):
    '''
    Select top K features of a category base on feature's Chi2 value
    Params:
        k_pos: num of features to select
        feat_val_dict: {word: chi2_val} of calculated chi2 values
    Returns:
        top_k_features: [] of Top K features from category
    '''
    
    sorted_feat_val_dict = sorted(feat_val_dict.iteritems(),key=operator.itemgetter(1), reverse=True)
#     writeToFile(sorted_feat_val_dict, "sorted_feat_val_dict.txt")
     
    chi2_threshold = sorted_feat_val_dict[top_k-1][1]
#     print "chi2_threshold: %s" % chi2_threshold
      
#     top_k_features = [x[0] for x in sorted_feat_val_dict if x[1]>=chi2_threshold]

#     if top_k == 1:
#         top_k_features = [x[0] for x in sorted_feat_val_dict if x[1]>=chi2_threshold]
#     else:
#         top_k_features = [x[0] for x in sorted_feat_val_dict if x[1]> chi2_threshold]
    
    
    top_k_features_dict = sorted_feat_val_dict[:top_k]
    top_k_features = [x[0] for x in top_k_features_dict] 
    
    return top_k_features_dict

def SelectTopKChi2Features(feat_val_dict, top_k):
    '''
    Select top K features of a category base on feature's Chi2 value
    Params:
        k_pos: num of features to select
        feat_val_dict: {word: chi2_val} of calculated chi2 values
    Returns:
        top_k_features: [] of Top K features from category, include features of same Kth chi2 val
        
    '''
    
    sorted_feat_val_dict = sorted(feat_val_dict.iteritems(),key=operator.itemgetter(1), reverse=True)
#     writeToFile(sorted_feat_val_dict, "sorted_feat_val_dict.txt")
    
    val = [v for w, v in feat_val_dict.iteritems()]
    val_list = list(set(val))
    sorted_val = sorted(val_list, reverse=True)
    
    percentile = top_k
    top_k = int(math.ceil((1-(float(percentile)/100.00))* len(sorted_val))) 
    print "percentile: %s" % percentile
    print "len of feature: %s" % len(sorted_val) 
    print "top_k: %s" % top_k
    
#     if top_k > len(sorted_val):
#         top_k = len(sorted_val)
    
    chi2_threshold = sorted_val[top_k-1]
    if chi2_threshold < 3.841:
        chi2_threshold = 3.841
        
    print "chi2_threshold: %s" % chi2_threshold
      
    top_k_features = [x[0] for x in sorted_feat_val_dict if x[1]>=chi2_threshold]

#     if top_k == 1:
#         top_k_features = [x[0] for x in sorted_feat_val_dict if x[1]>=chi2_threshold]
#     else:
#         top_k_features = [x[0] for x in sorted_feat_val_dict if x[1]> chi2_threshold]
    
    return top_k_features

def selectTweetIfFeatureExists(tweet_samples, sample_size, features, feat_type):
    selected_samples = []
    done = False
    for k in features:
        for tweet in tweet_samples:
            if tweet in selected_samples:
                continue
            if k in tweet[TWEET_FEATURES][feat_type]:
                if len(selected_samples)+1 <= sample_size: #check sample size
                    selected_samples.append(tweet)
                    last_feature = k
                    last_tweet = tweet    
#                 elif k == last_feature:
#                     selected_samples.append(tweet)

                else:
                    done = True
                    break   
        if done:
            break
    return selected_samples

if __name__ == '__main__':
    pass