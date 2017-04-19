'''
Created on Mar 8, 2014

@author: LIYING
'''
from sklearn.externals import joblib

from CS4242_Assg2.constants import SVM_X
from web.models import SVMStatesSentimental


def loadSentimentalASVM(category):
    return SVMStatesSentimental.objects.get(classifier_name=category)

def performSVMClassificationForSA(svm, svm_matrix):
    '''
    Performs a SVM classification and returns a positive or negative per category
    
    Parameters:
        svm: SVMClassifier object
        
    Returns:
        result list
    '''
    svmfilename = svm.state
    svm_classifier = joblib.load(svmfilename)
    
    X = svm_matrix[SVM_X]
    
    reslist = svm_classifier.predict(X).tolist()
    return reslist