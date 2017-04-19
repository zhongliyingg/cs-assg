'''
Created on Mar 8, 2014

@author: LIYING
'''
from CS4242_Assg2.constants import *
from svm.SATraining import getTweetFeatureMatrix

def getSVMMatrixForSA(featurematrix_sa, features_used, tweet_feature_list=None):
    '''
    Turns a FeatureMatrixClassifier into a SVM Ready matrix
    
    Parameters: 
        featurematrix_sa FeatureMatrixSentimental object
        tweet_feature_list : used for testing data input
    
    Returns:
        {SVM_X: [ ] , SVM_Y: [ ]}
    '''
    
    feature_to_id_map = featurematrix_sa.feature_to_id_map
    
#     if tweet_feature_list == None:
#         # Training
#         tweet_featureids_list = featurematrix_classifier.tweet_feature_ids_list
    
    feature_size = len(feature_to_id_map)
    svmmatrix = []
    labels = []
    if tweet_feature_list == None: #training
        tweet_fm_list = featurematrix_sa.tweet_feature_matrix_list
        for tweet_fm in tweet_fm_list:
            svmmatrixline = [0] * feature_size
            for feat_id, val in tweet_fm[TWEET_FEATURE_MATRIX].iteritems():
                svmmatrixline[feat_id] = val
            
            svmmatrix.append(svmmatrixline)
            labels.append(tweet_fm[LABEL])
            
    else: #testing
#         print tweet_feature_list
        for tweet in tweet_feature_list:
            svmmatrixline = [0] * feature_size
            tweet_fm = getTweetFeatureMatrix(tweet[TWEET_FEATURES], feature_to_id_map, features_used)
            for feat_id, val in tweet_fm.iteritems():
                svmmatrixline[feat_id] = val
                
            # No labels for classification data
            svmmatrix.append(svmmatrixline)
        
    return {SVM_X: svmmatrix, SVM_Y: labels }
