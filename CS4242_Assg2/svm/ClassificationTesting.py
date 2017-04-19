'''
Created on Feb 25, 2014

@author: simkerncheh
'''
from sklearn.externals import joblib
from web.models import SVMStatesClassifier, SVMStatesSentimental
from CS4242_Assg2.constants import SVM_X

def loadClassificationSVM(category):
    return SVMStatesClassifier.objects.get(classifier_name=category)

def performSVMClassification(svm, svm_matrix):
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
