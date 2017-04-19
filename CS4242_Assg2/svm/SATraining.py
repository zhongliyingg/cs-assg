'''
Created on Mar 8, 2014

@author: LIYING
'''
from sklearn import svm
from sklearn.externals import joblib

from CS4242_Assg2.constants import *
from svm.SVMHelper import generateFeatureIds
from web.models import FeatureMatrixSentimental, SVMStatesClassifier, \
    SVMStatesSentimental


def getTweetFeatureMatrix(tweet_features, feature_id_map, features_used):
    '''
    Get the matrix column ids and corresponding value for features in tweet
    Return:
        matrix_dict: { matrix_col_id : matrix_value}
    '''
    matrix_dict = {}
    for f in features_used:
        # TODO: whitelist
        if f == FEATURE_SA_REPLIES or f == FEATURE_SA_TEMPORAL:
            continue
        for word, value in tweet_features[f][FEATURE_VALUE].iteritems():
            if word in feature_id_map:
                matrix_col_id = feature_id_map[word]
                matrix_dict[matrix_col_id] = value
    return matrix_dict

def getFeatureMatrixForSA(category, tweet_set, features_list, features_used):
    '''
    Params:
        category: training category
        tweet_set: {label: tweets} of training tweets, tweets {TWEET_FULL: "", "TWEET_FEATURES": {}}
        features_list: [] of features
        features_used: [] of feature type constants from  CS4242_Assg2.constants 
    
    Return:
         FeatureMatrixClassifier object
    '''

    # Assign IDs to unique words
    feature_id_map = generateFeatureIds(features_list, 0)
    
    # For every tweet
    tweet_feature_matrix_list = []
    
    for label, tweets in tweet_set.iteritems():
        for tweet in tweets:
            tweet_feature_matrix = getTweetFeatureMatrix(tweet[TWEET_FEATURES], feature_id_map, features_used)
#             print tweet_feature_matrix
            tweet_feature_matrix_list.append({TWEET_FULL: tweet[TWEET_FULL],
                                           TWEET_FEATURE_MATRIX: tweet_feature_matrix,
                                           LABEL: label})
        
    feature_matrix = FeatureMatrixSentimental.objects.create(category=category,
                                                             feature_to_id_map=feature_id_map,
                                                             tweet_feature_matrix_list=tweet_feature_matrix_list)
    
    return feature_matrix

def createSVMForSA(category, featurematrix, svmmatrix, features_used):
    '''
    Creates and saves a SVM
    
    Params:
        category: category of svm
    
    Returns:
        SVM
        
    '''
    
    X = svmmatrix[SVM_X]
    Y = svmmatrix[SVM_Y]
    
    clf = svm.SVC(kernel='linear')
    clf.fit(X, Y)
    
    filename = '%s%s_SA_state.pkl' % (PATH_SVM_STATES, category)
    
    joblib.dump(clf, filename)
    
    svmstatesc = SVMStatesSentimental.objects.create(classifier_name=category, featurematrix=featurematrix,
                                                     features_enabled=features_used, state=filename)
    
    return svmstatesc
