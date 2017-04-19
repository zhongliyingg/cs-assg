'''
Created on Feb 23, 2014

@author: simkerncheh
'''
from CS4242_Assg2.constants import *
from console_debug.debug_methods import printresults, printresultsSA
from evaluation.evaluation import verifyGTForClassification, verifyGTForSA
from parser2.ParserCommon import splitfilebycategory
from web.helper.DatabaseTools import purgeFeaturesetsFromDB, \
    purgeSVMStatesFromDB
from web.helper.Jobs_Classifier import performTraining, performClassification
from web.helper.Jobs_SA import performSA, performTrainingForSA
import json

run_classifier = True
run_sa = False

if __name__ == '__main__':
    purgeFeaturesetsFromDB()
    purgeSVMStatesFromDB()

    # Training for SVM
    performTraining(PATH_TRAINING_DATA, PATH_GROUNDTRUTH_TRAINING, FEATURES_DEFAULT)
    
    
    # Training for SA
    features_used = [ FEATURE_SA_NEGATION, 
                 FEATURE_SA_EXCLAMATION_PRESENCE, 
                 FEATURE_SA_CAPS_PERCENTAGE, FEATURE_SA_CAPS_POLARITY, 
                 FEATURE_SA_POS, FEATURE_SA_POLARITY_SCORES,
                 FEATURE_SA_POLARITY_TEXT, FEATURE_SA_POLARITY_POS,  
                 FEATURE_TEXT, FEATURE_HASHTAG,  
                 FEATURE_SA_EMOTICONS, FEATURE_SA_EMOTICONS_POLARITY]
#                  FEATURE_SA_TEMPORAL, FEATURE_SA_REPLIES]
    features_used = FEATURES_SA_DEFAULT
    performTrainingForSA(PATH_TRAINING_DATA, PATH_GROUNDTRUTH_TRAINING, features_used)
    
    combined_results = performClassification(PATH_TESTING_DATA, FEATURES_DEFAULT)
    evaluation = verifyGTForClassification(PATH_GROUNDTRUTH_TESTING, combined_results)
    printresults(evaluation)
    
    organized_results = splitfilebycategory(PATH_TESTING_DATA, combined_results)
          
    final_combined_results = {}
    for category, value in organized_results.iteritems():
        # For each category
        combined_results = performSA(value, category)
        final_combined_results = dict(final_combined_results.items() + combined_results.items())
            
    evaluation = verifyGTForSA(PATH_GROUNDTRUTH_TESTING, final_combined_results)
    printresultsSA(evaluation)
     
    
    print 'done'
