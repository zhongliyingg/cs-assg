'''
Created on Feb 25, 2014

@author: simkerncheh
'''
from CS4242_Assg2.constants import *

def getTweetFeatureIDs(tweet_features, feature_id_map, features_used):
    '''
    Get feature IDs of given tweet features
    Params:
        tweet_features: dict of processed tweet features, { feat_type_contant: feat_content }
        feature_id_map: dict of features to assigned id, { feat: id }
        features_used: list of feature types in use, [] of feature type constants from CS4242_Assg2.constants
    Output:
        []
        list of feature ids
    '''
    
    feature_id_list = []
    
    if FEATURE_TEXT in features_used:
        for word in tweet_features[FEATURE_TEXT].iterkeys():
            if word in feature_id_map:
                feature_id_list.append(feature_id_map[word])
    
    if FEATURE_HASHTAG in features_used:        
        for ht in tweet_features[FEATURE_HASHTAG]:
            if ht in feature_id_map:
                feature_id_list.append(feature_id_map[ht])
    
    if FEATURE_GEOINFO in features_used:        
        geo = tweet_features[FEATURE_GEOINFO]
        if geo in feature_id_map:
            feature_id_list.append(feature_id_map[geo])
    
    
    if FEATURE_FOLLOWED_CATEGORIES in features_used:
        fc_list = tweet_features[FEATURE_FOLLOWED_CATEGORIES]
        for fc in fc_list:
    #             fullname = 'follows_%s' % (fc)
            if fc in feature_id_map:
                feature_id_list.append(feature_id_map[fc])

    # Extract user-temporal info
#         if use_temporal_info:
#             created_at = tweet[FEATURE_CREATED_AT]
#             userid = int(tweet[FEATURE_USER])
#             createOrUpdateTemporalInfo(userid, category, dateutil.parser.parse(created_at))

    if FEATURE_USER in features_used:
        user = tweet_features[FEATURE_USER]
        if user in feature_id_map:
            feature_id_list.append(feature_id_map[user])
        
    if FEATURE_USER_MENTIONS in features_used:
        user_ment = tweet_features[FEATURE_USER_MENTIONS]
        for um in user_ment:
            if um in feature_id_map:
                feature_id_list.append(feature_id_map[um])
                
    if FEATURE_CATEGORY in features_used:
        cat_feat = tweet_features[FEATURE_CATEGORY]
        for cat in cat_feat:
            if cat in feature_id_map:
                feature_id_list.append(feature_id_map[cat])
    
    return feature_id_list

def getSVMMatrixForClassification(featurematrix_classifier, tweet_feature_list=None, features_used=FEATURES_DEFAULT):
    '''
    Turns a FeatureMatrixClassifier into a SVM Ready matrix
    
    Parameters: 
        FeatureMatrixClassifier featurematrix_classifier
        tweet_feature_list : used for testing data input
    
    Returns:
        {SVM_X: [ ] , SVM_Y: [ ]}
    '''
    
    feature_to_id_map = featurematrix_classifier.feature_to_id_map
    
    if tweet_feature_list == None:
        # Training
        tweet_featureids_list = featurematrix_classifier.tweet_feature_ids_list
    
    feature_size = len(feature_to_id_map)
    svmmatrix = []
    labels = []
    if tweet_feature_list == None: #training
        for tweet_featids in tweet_featureids_list:
            svmmatrixline = [0] * feature_size
            feature_id_list = tweet_featids[TWEET_FEATURE_MATRIX]
            for feat in feature_id_list:
                # By presence
                svmmatrixline[feat] = 1
            
            svmmatrix.append(svmmatrixline)
            labels.append(tweet_featids[LABEL])
            
    else: #testing
#         print tweet_feature_list
        for tweet in tweet_feature_list:
            svmmatrixline = [0] * feature_size
            feature_id_list = getTweetFeatureIDs(tweet[TWEET_FEATURES], feature_to_id_map, features_used)
            for feat in feature_id_list:
                # By presence
                svmmatrixline[feat] = 1
                
            # No labels for classification data
            svmmatrix.append(svmmatrixline)
        
    return {SVM_X: svmmatrix, SVM_Y: labels }
