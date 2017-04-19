'''
Created on 28 Feb, 2014

@author: simkerncheh
'''
from CS4242_Assg2.constants import *
from console_debug.debug_methods import writeDebugListToFile, \
    writeDebugCountDictToFile, debugPrint
from django.db import connection
from feature_selection.Selection import selectFeatureByChi2, \
    selectTweetIfFeatureExists
from parser2.Parser import parseLabelFile, getKeyInfoForClassifier, \
    extractFeaturesFromTweet
from svm.ClassificationHelper import getSVMMatrixForClassification
from svm.ClassificationTesting import performSVMClassification
from svm.ClassificationTraining import getFeatureMatrix, createSVM
from web.helper.DatabaseTools import updateJobStatus
from web.models import SVMStatesClassifier, JobStatus
import codecs
import json
import traceback




def performTraining(data_filename, label_filename, features_used=FEATURES_DEFAULT, job_id=None):
    try:
        # extract & preprocess features
        debugPrint("feature extraction and preprocessing...")
        if job_id != None:
            connection.close()
            jobstatus = JobStatus.objects.get(id=job_id)
            updateJobStatus(jobstatus, "Acquiring Key info")
            
        gen = parseLabelFile(label_filename)
        categories_list = gen['categories']
        groundtruth_list = gen['groundtruth_list']
        all_keyinfo = getKeyInfoForClassifier(data_filename, categories_list, groundtruth_list, features_used) 
        
        for category, keyinfo in all_keyinfo.iteritems():
            debugPrint("training category: %s" % category)
            if job_id != None:
                updateJobStatus(jobstatus, "Training category: %s" % (category))
            pos_tweets = keyinfo[POSITIVE][PROCESSED_TWEETS]
            pos_sample_size = len(pos_tweets)
            neg_tweets = keyinfo[NEGATIVE][PROCESSED_TWEETS]
            neg_sample_size = len(neg_tweets)
            
            # feature selection
            debugPrint(">> feature selection")
            if job_id != None:
                updateJobStatus(jobstatus, "Feature selection on category: %s" % (category))
            select_results = selectTrainingFeaturesAndNegSamples(keyinfo, features_used, pos_sample_size, category)
            selected_feat = select_results[0]
            selected_neg_tweets = select_results[1]
    #         
            writeDebugListToFile("%s_selected_feat.txt" % category, selected_feat)
            writeDebugListToFile("%s_selected_neg_tweets.txt" % category, selected_neg_tweets)
            writeDebugListToFile("%s_pos_tweets.txt" % category, pos_tweets)
            
            # create feature matrix for each tweet
            debugPrint(">> get feature matrix")
            training_tweets = {POSITIVE: pos_tweets, NEGATIVE: selected_neg_tweets }
            feature_matrix = getFeatureMatrix(category, training_tweets, selected_feat, features_used)
            writeDebugCountDictToFile("%s_feature_to_id_map.txt" % category, feature_matrix.feature_to_id_map)
            writeDebugListToFile("%s_tweet_feature_ids_list.txt" % category, feature_matrix.tweet_feature_ids_list)
            
            debugPrint('feature count: %s' % len(feature_matrix.feature_to_id_map))
            debugPrint("positive tweets count: %s" % pos_sample_size)
            debugPrint("negative tweets count: %s" % len(selected_neg_tweets))
            
            # create svm matrix
            debugPrint(">> create svm matrix")
            
            if job_id != None:
                updateJobStatus(jobstatus, "Creating SVM Matrix for category %s" % (category))
            svm_matrix = getSVMMatrixForClassification(feature_matrix)
            writeDebugListToFile("%s_svm_matrix_X.txt" % category, svm_matrix[SVM_X])
            writeDebugListToFile("%s_svm_matrix_Y.txt" % category, svm_matrix[SVM_Y])
            createSVM(category, feature_matrix, svm_matrix)
            
            debugPrint("training completed for category: %s" % category)
            if job_id != None:
                updateJobStatus(jobstatus, "Training completed for category: %s" % (category))
        
        if job_id != None:
            updateJobStatus(jobstatus, "Completed!")
            
    except:
        traceback.print_exc(file=open("%s/svmstates/errlog.txt" % (BASE_DIR),"a"))
        

def performClassification(test_input_filename, features_used=FEATURES_DEFAULT):
    '''
    Returns:
        combined_results:
            {
                'apple': [0,0,1,0...],
                'twitter': [0,0,0,...],
            }
    '''
    with codecs.open(test_input_filename, encoding='cp1252') as k:
        tweet_features_list = []
        categorieslist = []
        svmstates = SVMStatesClassifier.objects.all()
        for svm in svmstates:
            categorieslist.append(svm.classifier_name)
        for line in k:
            json_data = json.loads(line, encoding='cp1252')
            featureline = extractFeaturesFromTweet(json_data, categorieslist, features_used)
            # {'tweet': This was a triumph, 'features': {FEATURE_TEXT: __ , 'geolocation' : __ }}
            tweet_features_list.append(featureline)
        writeDebugListToFile("test_tweets_feature.txt", tweet_features_list)
        
        #    For each svm
        combined_results = {}
        for svm in svmstates:
            featurematrix_classifier = svm.featurematrix
            svm_matrix = getSVMMatrixForClassification(featurematrix_classifier, tweet_features_list)
            writeDebugListToFile("%s_test_svm_matrix.txt" % featurematrix_classifier.category, svm_matrix[SVM_X])
            
#             print type(featurematrix_classifier.category)
            reslist = performSVMClassification(svm, svm_matrix)
            combined_results[svm.classifier_name] = reslist
        
        for key, value in combined_results.iteritems():
            writeDebugListToFile("%s_results.txt" % key, value)
            
        return combined_results
            
def selectFeatureAndNegSamples(keyinfo, feat_type, feat_size, neg_sample_by_feat_size, debug_category=''):
    '''
    High level function to select features of type and select negative samples using the selected features
    Params:
        keyinfo: output from getKeyInfoForClassifier
        feat_type: name of feature, from CS4242_Assg2.constants
        feat_size: number of features to select
        neg_sample_by_feat_size: number of negative samples to select 
        debug_category (optional): category name for writing debug files
    Output:
        tuple
        [0]: [] of selected features
        [1]: [] of selected negative samples
    '''
    pos_tweets = keyinfo[POSITIVE][PROCESSED_TWEETS]
    pos_sample_size = len(pos_tweets)
    neg_tweets = keyinfo[NEGATIVE][PROCESSED_TWEETS]
    neg_sample_size = len(neg_tweets)
    
    sel_feat = []
    sel_neg_by_feat = []
    
    if feat_type in keyinfo[UNIQUE_FEATURES] \
        and feat_type in keyinfo[POSITIVE][FEATURES] \
        and feat_type in keyinfo[NEGATIVE][FEATURES]:   
        unique_feat = keyinfo[UNIQUE_FEATURES][feat_type]
        pos_feat = keyinfo[POSITIVE][FEATURES][feat_type]
        neg_feat = keyinfo[NEGATIVE][FEATURES][feat_type]
    
        chi2_feat = selectFeatureByChi2(unique_feat, pos_feat, neg_feat, pos_sample_size, neg_sample_size, feat_size)
        writeDebugListToFile("%s_%s_chi2_sel_feat.txt" % (debug_category, feat_type), chi2_feat)
        
        sel_feat = [x[0] for x in chi2_feat]
        writeDebugListToFile("%s_%s_chi2_sel_feat_only.txt" % (debug_category, feat_type), sel_feat)
        
        debugPrint("%s feature count (intial): %s" % (feat_type, len(pos_feat)))
        debugPrint("%s feature count (selected): %s" % (feat_type, len(sel_feat)))
        
        sel_neg_by_feat = selectTweetIfFeatureExists(neg_tweets, neg_sample_by_feat_size, sel_feat, feat_type)
        debugPrint("%s selected neg tweet count: %s" % (feat_type, len(sel_neg_by_feat)))
    
    else:
        debugPrint("%s not in use" % feat_type)
        
    return (sel_feat, sel_neg_by_feat)

def selectTrainingFeaturesAndNegSamples(keyinfo, features_used, rel_sample_size, debug_category=''):
    '''
    High(er) level function to select features of all types in use, and select negative samples using features selected
    Params:
        keyinfo: output from getKeyInfoForClassifier
        features_used: [] of name of features in used, from CS4242_Assg2.constants
        rel_sample_size: relative number of negative samples to select 
        debug_category (optional): category name for writing debug files
    Output:
        tuple
        [0]: [] of selected features
        [1]: [] of selected negative samples
    '''
    selected_feat = []
    selected_neg_tweets = []
    
    if FEATURE_TEXT in features_used:
        selected_results = selectFeatureAndNegSamples(keyinfo, FEATURE_TEXT, 200, rel_sample_size, debug_category)
        selected_feat += selected_results[0]
        selected_neg_tweets += selected_results[1]
    
    if FEATURE_HASHTAG in features_used:
        selected_results = selectFeatureAndNegSamples(keyinfo, FEATURE_HASHTAG, 20, rel_sample_size / 4, debug_category)
        selected_feat += selected_results[0]
        selected_neg_tweets += selected_results[1]
    
    if FEATURE_GEOINFO in features_used:
        selected_results = selectFeatureAndNegSamples(keyinfo, FEATURE_GEOINFO, 3, rel_sample_size / 2, debug_category)
        selected_feat += selected_results[0]
        selected_neg_tweets += selected_results[1]
    
    if FEATURE_CATEGORY in features_used:
        selected_results = selectFeatureAndNegSamples(keyinfo, FEATURE_CATEGORY, 4, rel_sample_size / 4, debug_category)
        selected_feat += selected_results[0]
        selected_neg_tweets += selected_results[1]
        
    if FEATURE_USER_MENTIONS in features_used:
        selected_results = selectFeatureAndNegSamples(keyinfo, FEATURE_USER_MENTIONS, 20, rel_sample_size / 4, debug_category)
        selected_feat += selected_results[0]
        selected_neg_tweets += selected_results[1]
    
    
    selected_neg_tweets_remove_dup = {t[TWEET_FULL]:t for t in selected_neg_tweets}.values()
    
    return (selected_feat, selected_neg_tweets_remove_dup)
