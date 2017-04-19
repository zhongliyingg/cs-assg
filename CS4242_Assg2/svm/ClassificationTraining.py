'''
Created on Feb 25, 2014

@author: simkerncheh
'''

from sklearn import svm
from sklearn.externals import joblib

from CS4242_Assg2.constants import *
from svm.ClassificationHelper import getTweetFeatureIDs
from svm.SVMHelper import generateFeatureIds
from web.models import FeatureMatrixClassifier, SVMStatesClassifier


def getFeatureMatrix(category, tweet_set, features_list, features_used):
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
    tweet_feature_ids_list = []
    
    for label, tweets in tweet_set.iteritems():
        for tweet in tweets:
            features_id_list = getTweetFeatureIDs(tweet[TWEET_FEATURES], feature_id_map, features_used)
            tweet_feature_ids_list.append({TWEET_FULL: tweet[TWEET_FULL], TWEET_FEATURE_MATRIX: features_id_list, LABEL: label})
        
    feature_matrix = FeatureMatrixClassifier.objects.create(category=category, feature_to_id_map=feature_id_map, tweet_feature_ids_list=tweet_feature_ids_list)
    
    return feature_matrix

def createSVM(category, featurematrix_classifier, svmmatrix):
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
    
    filename = '%s%s_state.pkl' % (PATH_SVM_STATES, category)
    
    joblib.dump(clf, filename)
    
    svmstatesc = SVMStatesClassifier.objects.create(classifier_name=category, featurematrix=featurematrix_classifier,
                                       state=filename)
    
    return svmstatesc

if __name__ == '__main__':
    pass
