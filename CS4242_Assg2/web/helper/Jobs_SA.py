'''
Created on Mar 7, 2014

@author: LIYING
'''
import base64
import base64
import codecs
import codecs
from collections import OrderedDict
import copy
import datetime
from itertools import chain, chain
import json
import json
import operator
import pickle
import pickle
import traceback

import dateutil.parser
from django.db import connection, connection
from django.utils import timezone, timezone

from CS4242_Assg2.constants import *
from console_debug.debug_methods import writeDebugListToFile, \
    writeDebugCountDictToFile, debugPrint
from evaluation.evaluation import verifyGTForSA
from feature_selection.Chi2StatisticsSA import calculateChi2ValuesSA
from feature_selection.SelectionSA import selectTweetsForSA
from parser2.ParserCommon import parseLabelFile, splitfilebycategory
from parser2.ParserSA import getKeyInfoForSA, extractSentiFeaturesFromTweet
from svm.SAHelper import getSVMMatrixForSA
from svm.SATesting import performSVMClassificationForSA
from svm.SATraining import getFeatureMatrixForSA, createSVMForSA
from web.helper.DatabaseTools import updateJobStatus
from web.helper.Jobs_Classifier import performClassification
from web.models import SVMStatesClassifier, SVMStatesSentimental, JobStatusSA, \
    SAResults, JobStatus
    
import copy
import datetime
import dateutil.parser
import json
import operator
import traceback

def selectTweetIfFeatureExistsSA(tweet_set, sample_size, features, feat_type):
    selected_samples = {}
    done = False

    for class_svm, class_svm_tweets in tweet_set.iteritems():
        selected_samples[class_svm] = []
        if len(class_svm_tweets) < sample_size:
            selected_samples[class_svm] = class_svm_tweets
            continue
#             sample_size = len(class_svm_tweets)
        check_for_features = []
        for other_class_svm, class_svm_tweets in tweet_set.iteritems():
            if other_class_svm != class_svm:
                check_for_features += features[other_class_svm]
        for k in check_for_features:
            for tweet in class_svm_tweets:
                if tweet in selected_samples[class_svm]:
                    continue
                if k in tweet[TWEET_FEATURES][feat_type][FEATURE_VALUE]:
#                     print k, tweet[TWEET_FEATURES][feat_type][FEATURE_VALUE]
#                     selected_samples[class_svm].append(tweet)
                    if len(selected_samples[class_svm])+1 <= sample_size: #check sample size
                        selected_samples[class_svm].append(tweet)
                    else:
                        done = True
                        break   
            if done:
                break
        print class_svm, len(selected_samples[class_svm])
    return selected_samples

def selectFeature(unique_feat, feature_set, sample_size_set, top_k_for_each_set):
    training_features = {CLASS_SVM_POSITIVE:[], CLASS_SVM_NEGATIVE:[],  CLASS_SVM_NEUTRAL:[]}
    senti_chi2 = calculateChi2ValuesSA(unique_feat, feature_set, sample_size_set)
    top_k_features = []
    for senti in senti_chi2:
        feat_val_dict = senti_chi2[senti]
        sorted_feat_val_dict = sorted(feat_val_dict.iteritems(),key=operator.itemgetter(1), reverse=True)
#         print sorted_feat_val_dict
        if top_k_for_each_set > len(sorted_feat_val_dict):
            top_k_for_each_set = len(sorted_feat_val_dict)
        top_k_features_dict = sorted_feat_val_dict[:top_k_for_each_set]
#         print top_k_features_dict
#         print len(top_k_features_dict)
        
        chi2_threshold = sorted_feat_val_dict[top_k_for_each_set-1][1]
        senti_k_features = [x for x in top_k_features_dict if x[1] >= chi2_threshold]
        top_k_features += senti_k_features
        training_features[senti] = [x[0] for x in top_k_features_dict if x[1] >= chi2_threshold]
            
    sorted_top_feat_dict = sorted(top_k_features,key=operator.itemgetter(1), reverse=True) 
    top_feat_dict = [x[0] for x in sorted_top_feat_dict]
    feat_no_dup = list(OrderedDict.fromkeys(top_feat_dict)) # remove duplicates
    return feat_no_dup, training_features

def selectFeaturesForTraining(keyinfo, feat_used):
    all_features = keyinfo[UNIQUE_FEATURES]
    sample_size_set = {CLASS_SVM_POSITIVE: len(keyinfo[CLASS_SVM_POSITIVE][PROCESSED_TWEETS]),
                       CLASS_SVM_NEUTRAL: len(keyinfo[CLASS_SVM_NEUTRAL][PROCESSED_TWEETS]),
                       CLASS_SVM_NEGATIVE: len(keyinfo[CLASS_SVM_NEGATIVE][PROCESSED_TWEETS])}
    tweet_set = {CLASS_SVM_POSITIVE: keyinfo[CLASS_SVM_POSITIVE][PROCESSED_TWEETS],
                   CLASS_SVM_NEUTRAL: keyinfo[CLASS_SVM_NEUTRAL][PROCESSED_TWEETS],
                   CLASS_SVM_NEGATIVE: keyinfo[CLASS_SVM_NEGATIVE][PROCESSED_TWEETS]}
    
#     print all_features
    selected_feat = []
    training_tweets = {CLASS_SVM_POSITIVE: [], CLASS_SVM_NEUTRAL: [], CLASS_SVM_NEGATIVE:[]}
    size = min(len(tweet_set[CLASS_SVM_POSITIVE]), len(tweet_set[CLASS_SVM_NEGATIVE]), len(tweet_set[CLASS_SVM_NEUTRAL]))
    max_size = 2*size
    if max_size < 100:
        max_size = 100
#     print max_size
    for feat_type in feat_used:
        # TODO: whitelist
        if feat_type == FEATURE_SA_REPLIES or feat_type==FEATURE_SA_TEMPORAL:
            continue
        feature_set = {POLARITY_POSITIVE: keyinfo[CLASS_SVM_POSITIVE][FEATURES][feat_type],
                       POLARITY_NEUTRAL: keyinfo[CLASS_SVM_NEUTRAL][FEATURES][feat_type],
                       POLARITY_NEGATIVE: keyinfo[CLASS_SVM_NEGATIVE][FEATURES][feat_type]}
              
        if feat_type in all_features:
#             if feat_type == FEATURE_TEXT:
#                 print FEATURE_TEXT
#                 sel_feat_info = selectFeature(all_features[feat_type], feature_set, sample_size_set, 500)
#                 sel_feat = sel_feat_info[0]
#                 sel_tweet = selectTweetIfFeatureExistsSA(tweet_set, max_size, sel_feat_info[1], feat_type)
#                 for class_svm in training_tweets:
#                     training_tweets[class_svm] += sel_tweet[class_svm]
#                     debugPrint("%s class svm tweet count: %s" % (class_svm, len(sel_tweet[class_svm])))
#              
#             elif feat_type == FEATURE_HASHTAG:    
#                 print FEATURE_HASHTAG
#                 sel_feat_info = selectFeature(all_features[feat_type], feature_set, sample_size_set, 200)
#                 sel_feat = sel_feat_info[0]
#                 sel_tweet = selectTweetIfFeatureExistsSA(tweet_set, max_size, sel_feat_info[1], feat_type)
#                 for class_svm in training_tweets:
#                     training_tweets[class_svm] += sel_tweet[class_svm]
#                     debugPrint("%s class svm tweet count: %s" % (class_svm, len(sel_tweet[class_svm])))
                     
#             elif feat == FEATURE_SA_EMOTICONS:
#                 sel_feat = selectFeature(all_features[feat], feature_set, sample_size_set, 10)
#             else:
            sel_feat = all_features[feat_type]
            selected_feat += sel_feat
            debugPrint("%s sa feature count: %s" % (feat_type, len(sel_feat)))
            
#     for class_svm in training_tweets:
#         class_tweets = training_tweets[class_svm]
#         training_tweets[class_svm] = {t[TWEET_FULL]:t for t in class_tweets}.values()
#         debugPrint("%s class svm tweet count: %s" % (class_svm, len(training_tweets[class_svm])))
    
    return selected_feat, training_tweets



def selectFeatureIfExistsInTweet(selected_tweets_set, all_features, feat_type):
    sel_feat = []
#     print feat_type
    for f in all_features[feat_type].iterkeys():
        for label, tweet_set in selected_tweets_set.iteritems():
            appended_feat = False
            for tweet in tweet_set:
                if f in tweet[TWEET_FEATURES][feat_type][FEATURE_VALUE]:
                    sel_feat.append(f)
                    appended_feat = True
                    break
            if appended_feat:
                break
    return sel_feat

# def selectFeaturesForSA(keyinfo, selected_tweets_set, features_used):
#     all_features = keyinfo[UNIQUE_FEATURES]
#     selected_feat = []
#     for feat_type in features_used:
#         if feat_type == POLARITY_WORD:
#             continue
#         if feat_type in all_features:
#             if feat_type == FEATURE_TEXT:
#                 sel_feat = selectFeatureIfExistsInTweet(
#                                     selected_tweets_set, all_features, feat_type)
#                         
#             elif feat_type == FEATURE_HASHTAG:
#                 sel_feat = selectFeatureIfExistsInTweet(
#                                     selected_tweets_set, all_features, feat_type)
#             
#             elif feat_type == FEATURE_SA_EMOTICONS:
#                 sel_feat = selectFeatureIfExistsInTweet(
#                                     selected_tweets_set, all_features, feat_type)
#             else:
#                 sel_feat = all_features[feat_type]
#                 
#             selected_feat += sel_feat
#             debugPrint("%s sa feature count: %s" % (feat_type, len(sel_feat)))
#     return selected_feat

def performTrainingForSA(data_filename, label_filename, features_used=FEATURES_SA_DEFAULT, job_id=None):
    # extract & preprocess features
    try:
        debugPrint("feature extraction and preprocessing...")
        if job_id != None:
            connection.close()
            jobstatus = JobStatusSA.objects.get(id=job_id)
        
        gen = parseLabelFile(PATH_GROUNDTRUTH_TRAINING)
        categories_list = gen['categories']
        groundtruth_list = gen['groundtruth_list']
        all_keyinfo = getKeyInfoForSA(PATH_TRAINING_DATA, categories_list, groundtruth_list, features_used)  # A test for unicode errors
        
        for category, keyinfo in all_keyinfo.iteritems():
            debugPrint("training category: %s" % category)
            if job_id != None: 
                updateJobStatus(jobstatus, "Training Category: %s" % category)
            pos_tweets = keyinfo[CLASS_SVM_POSITIVE][PROCESSED_TWEETS]
            neg_tweets = keyinfo[CLASS_SVM_NEGATIVE][PROCESSED_TWEETS]
            neu_tweets = keyinfo[CLASS_SVM_NEUTRAL][PROCESSED_TWEETS]
            
    #         size = min(len(pos_tweets), len(neg_tweets), len(neu_tweets))
    #         max_size = 2*size
    #         if max_size < 100:
    #             max_size = 100
    #         print size, max_size
            
            # feature selection
            debugPrint(">> feature selection")
            
            # create feature matrix for each tweet
            debugPrint(">> get feature matrix")
            training_tweets = {CLASS_SVM_POSITIVE: pos_tweets,
                               CLASS_SVM_NEGATIVE: neg_tweets,
                               CLASS_SVM_NEUTRAL: neu_tweets}
            
            selected_feat_tweets = selectFeaturesForTraining(keyinfo, features_used)
            selected_feat = selected_feat_tweets[0]
#             training_tweets = selected_feat_tweets[1]
            
    #         selected_feat = selectFeaturesForSA(keyinfo, training_tweets, features_used)
            writeDebugListToFile("%s_sa_selected_feat.txt" % category, selected_feat)
            writeDebugListToFile("%s_sa_pos_tweets.txt" % category, pos_tweets)
            writeDebugListToFile("%s_sa_neg_tweets.txt" % category, neg_tweets)
            writeDebugListToFile("%s_sa_neu_tweets.txt" % category, neu_tweets)
            
            feature_matrix = getFeatureMatrixForSA(category, training_tweets, selected_feat, features_used)
            
            debugPrint("feature count: %s" % len(feature_matrix.feature_to_id_map))
            writeDebugCountDictToFile("%s_sa_feature_to_id_map.txt" % category, feature_matrix.feature_to_id_map)
            writeDebugListToFile("%s_sa_tweet_feature_matrix_list.txt" % category, feature_matrix.tweet_feature_matrix_list)
            
            # create svm matrix
            debugPrint(">> create svm matrix")
            if job_id != None:
                updateJobStatus(jobstatus, "Creating SVM Matrix for category %s" % (category))
            svm_matrix = getSVMMatrixForSA(feature_matrix, features_used)
            createSVMForSA(category, feature_matrix, svm_matrix, features_used)
            writeDebugListToFile("%s_sa_svm_matrix_X.txt" % category, svm_matrix[SVM_X])
            writeDebugListToFile("%s_sa_svm_matrix_Y.txt" % category, svm_matrix[SVM_Y])
            
            debugPrint("training completed for category: %s" % category)
            if job_id != None:
                updateJobStatus(jobstatus, "Training completed for category: %s" % (category))
            
            # TODO: remove!
    #         break
        
        if job_id != None:
            updateJobStatus(jobstatus, "Completed!")
    except:
        traceback.print_exc(file=open("%s/svmstates/errlog.txt" % (BASE_DIR),"a"))


def performSA(test_data_list, category=None):
    '''
    Performs Sentimental Analysis on a given list of json tweets.
    
    Params:
        category: category in which input data belongs to.
                    None if uncategorized
    
    Returns:
    {
        'twitter': [[{TWEET_ID: id, TWEET_FULL: 'lalala', 
                              FEATURE_CREATED_AT: 'Sun Oct 16 22:28:08 +0000 2011', TWEET_USER_ID: 14883342}], [0,1,2],],
        'microsoft':[]
    }
    '''
    

    tweet_features_list = []
    tweet_id_list = []
    svmstates = SVMStatesSentimental.objects.all()
    debugPrint(">> Extracting features")
    
    for line in test_data_list:
        json_data = json.loads(line, encoding='cp1252')
        featureline = extractSentiFeaturesFromTweet(json_data)
        # {'tweet': This was a triumph, 'features': {FEATURE_TEXT: __ , 'geolocation' : __ }}
        # check if reply, combine features if nec
        tweet_features_list.append(featureline)
        tweet_id_list.append({TWEET_ID: json_data['id_str'], TWEET_FULL: json_data['text'], 
                              FEATURE_CREATED_AT: json_data['created_at'], TWEET_USER_ID: json_data['user']['id']})
#         writeDebugListToFile("test_tweets_feature.txt", tweet_features_list)
   
    tweet_features_list_replyconcat = copy.deepcopy(tweet_features_list)
#     print tweet_features_list_replyconcat
    for featureline in tweet_features_list_replyconcat:
        if featureline[TWEET_FEATURES][FEATURE_SA_REPLY_TO_ID] != "":
            for fline2 in tweet_features_list_replyconcat:
                if fline2[TWEET_FEATURES][FEATURE_SA_TWEETID_STR] == featureline[TWEET_FEATURES][FEATURE_SA_REPLY_TO_ID]:
                    # if ids match, featureline is a reply to fline2
                    for key, value in fline2[TWEET_FEATURES].iteritems():
                        if key != FEATURE_SA_TWEETID_STR and key != FEATURE_SA_REPLY_TO_ID and key != FEATURE_SA_CAPS_PERCENTAGE:
  
                            for key2, value2 in value[FEATURE_VALUE].iteritems():
                                  
                                if key2 not in featureline[TWEET_FEATURES][key][FEATURE_VALUE]:
                                    featureline[TWEET_FEATURES][key][FEATURE_VALUE][key2] = 0
                                  
                                featureline[TWEET_FEATURES][key][FEATURE_VALUE][key2] += value2
    
    #    For each svm
    debugPrint(">> Classifying with SVM")
    combined_results = {}
    for svm in svmstates:
        if category is None or category == svm.classifier_name:
            featurematrix_classifier = svm.featurematrix
            features_enabled = svm.features_enabled
            
            debugPrint("Classifying for %s" % featurematrix_classifier.category)
            if FEATURE_SA_REPLIES in features_enabled:
                svm_matrix = getSVMMatrixForSA(featurematrix_classifier, features_enabled, tweet_features_list_replyconcat)
            else:
                svm_matrix = getSVMMatrixForSA(featurematrix_classifier, features_enabled, tweet_features_list)
    #             writeDebugListToFile("%s_test_svm_matrix.txt" % featurematrix_classifier.category, svm_matrix[SVM_X])
            
            debugPrint("Perform SVM Classification for %s" % svm.classifier_name)
            reslist = performSVMClassificationForSA(svm, svm_matrix)
            
    
#         for key, value in combined_results.iteritems():
#             writeDebugListToFile("%s_results.txt" % key, value)

            # temporal info
#             print features_enabled
            if FEATURE_SA_TEMPORAL in features_enabled:
#                 print "ti enabled"
                ti_dict = {}
                for idx, res in enumerate(reslist):
                    user = tweet_id_list[idx][TWEET_USER_ID]
                    created_at = tweet_id_list[idx][FEATURE_CREATED_AT]
                    
                    if user in ti_dict:
                        # temporal info hit, update
                        
                        start = ti_dict[user]['last_tweet_time'] - datetime.timedelta(hours=TEMPORAL_INFO_TIMEFRAME_MINS)
                        end = ti_dict[user]['last_tweet_time'] + datetime.timedelta(hours=TEMPORAL_INFO_TIMEFRAME_MINS)
                        if start <= ti_dict[user]['last_tweet_time'] <= end:
                            reslist[idx] = ti_dict[user]['sentiment']
                            
                        ti_dict[user]['last_tweet_time'] = dateutil.parser.parse(created_at)
                    else:
                        # update and continue
                        ti_dict[user] = {'sentiment': res, 'last_tweet_time': dateutil.parser.parse(created_at)}
                          
            combined_results[svm.classifier_name] = (tweet_id_list, reslist)
                # incomplete
    return combined_results


###### METHOD SHOULD ONLY BE CALLED FROM HTTP REQUEST ######
def runCategorization(test_file_path, jobstatus):
    '''
    Categorizes and Determine Sentiments of input tweet file in JSON format.
    '''
    connection.close()
    updateJobStatus(jobstatus, "Performing Classification. This may take a while...")
    combined_results = performClassification(test_file_path, FEATURES_DEFAULT)
    organized_results = splitfilebycategory(test_file_path, combined_results)
    
    final_combined_results = {}
    for category, value in organized_results.iteritems():
        # For each category
        updateJobStatus(jobstatus, "Performing Sentimental Analysis on category %s." % (category))
        combined_results = performSA(value, category)
        final_combined_results = dict(chain(final_combined_results.items() + combined_results.items())) 
    
    updateJobStatus(jobstatus, "Tabulating Results") 
    db_results = {}
   
    for category, tweet_tuple in final_combined_results.iteritems():
        db_results[category] = []
        tweet_id_text_list = tweet_tuple[0]
        svm_result = tweet_tuple[1]
        for idx, res in enumerate(svm_result):
            positive = 0
            neutral = 0
            negative = 0
            if res == CLASS_SVM_POSITIVE:
                positive = 1
            elif res == CLASS_SVM_NEUTRAL:
                neutral = 1
            elif res == CLASS_SVM_NEGATIVE:
                negative = 1
            db_results[category].append({TWEET_FULL: tweet_id_text_list[idx][TWEET_FULL].encode('utf-8'), POLARITY_POSITIVE: positive,
                                     POLARITY_NEUTRAL: neutral, POLARITY_NEGATIVE:negative})
    svms = SVMStatesSentimental.objects.all()
    if svms:
        features_enabled_list = svms[0].features_enabled
#         print db_results
#         b1 = base64.b64encode(pickle.dumps(db_results))
#         value = pickle.loads(base64.b64decode(b1))
#         print value
        SAResults.objects.create(job_id=jobstatus.id, date=timezone.now(), svmresults=db_results,
                                 features_enabled=features_enabled_list,
                                 final_combined_results=final_combined_results)
        
        updateJobStatus(jobstatus, "Completed!")

def runEvaluation(test_groundtruth_path, results_id):
    
    saresult = SAResults.objects.get(job_id=results_id)
    combined_results = saresult.final_combined_results
    
    evaluation = verifyGTForSA(test_groundtruth_path, combined_results)
    '''
    From
    eval:
         {
            category: {
                'positive': {
                    'true_positive': [{TWEET_ID: tweet_id, TWEET_TEXT:saf, REMARKS:'correct'}],
                    'true_negative': [],
                    'false_positive': [],
                    'false_negative': [],
                    'precision': float,
                    'recall': float,
                    'f_one': float
                },
                neutral: {},
                negative: {}
                
            },
            ...
        }
    '''   
    '''
    To
    results: {
        'twitter':
            [
                {
                    TWEET_FULL: 'The snow glows white on the mountain tonight',
                    'positive': 1,
                    'neutral': 0,
                    'negative': 0
                    'remarks': "correct/false_positive/false_negative"
                }
            ]
    }
    
    evalmetrics: {
        'twitter':{
            'positive':{
                'precision': float,
                'recall': float,
                'f_one': float,
                'true_positive': int,
                'true_negative': int,
                'false_positive': int,
                'false_negative': int
            },
            'neutral': {...
            }
        }
    }
    '''
    new_combined_results = {}
    evalmetrics = {}
    
    for category, hm in evaluation.iteritems():
        new_combined_results[category] = []
        evalmetrics[category] = {}
        
        positive_map = hm[POLARITY_POSITIVE] # {'true_positive': [{TWEET_FULL:..., TWEET_ID: 123}], 'true_negative':... }
        neutral_map = hm[POLARITY_NEUTRAL]
        neg_map = hm[POLARITY_NEGATIVE]
        evalmetrics[category][POLARITY_POSITIVE] = {}
        evalmetrics[category][POLARITY_NEUTRAL] = {}
        evalmetrics[category][POLARITY_NEGATIVE] = {}
        
        
        populateNewResults(positive_map, new_combined_results, evalmetrics, category, POLARITY_POSITIVE)
        populateNewResults(neutral_map, new_combined_results, evalmetrics, category, POLARITY_NEUTRAL)
        populateNewResults(neg_map, new_combined_results, evalmetrics, category, POLARITY_NEGATIVE)
        
        
    saresult.svmresults = new_combined_results
    saresult.evalmetrics = evalmetrics
    saresult.save()
    
def populateNewResults(polarity_map, new_combined_results, evalmetrics, category, polarity):
    for key, item in polarity_map.iteritems():
            
        if key == 'true_positive' or key == 'true_negative' or key == 'false_positive' or key == 'false_negative':
            if key != 'true_negative' and key != 'false_negative':
                for element in item:
                    if element[ORIG_RESULT] == CLASS_SVM_POSITIVE:
                        new_combined_results[category].append({TWEET_FULL: element[TWEET_FULL], POLARITY_POSITIVE: 1, 
                                                   POLARITY_NEGATIVE:0, POLARITY_NEUTRAL:0, REMARKS: element[REMARKS]})
                    elif element[ORIG_RESULT] == CLASS_SVM_NEUTRAL:
                        new_combined_results[category].append({TWEET_FULL: element[TWEET_FULL], POLARITY_POSITIVE: 0, 
                                                   POLARITY_NEGATIVE:0, POLARITY_NEUTRAL:1, REMARKS: element[REMARKS]})
                    elif element[ORIG_RESULT] == CLASS_SVM_NEGATIVE:
                        new_combined_results[category].append({TWEET_FULL: element[TWEET_FULL], POLARITY_POSITIVE: 0, 
                                                   POLARITY_NEGATIVE:1, POLARITY_NEUTRAL:0, REMARKS: element[REMARKS]})
                        
            evalmetrics[category][polarity][key] = len(item)
        else:
            evalmetrics[category][polarity][key] = item
                

if __name__ == "__main__":
#     js = JobStatus.objects.create()
#     runCategorization(PATH_TESTING_DATA, js)
#     runEvaluation(PATH_GROUNDTRUTH_TESTING, js.id)
#     print SAResults.objects.get(job_id=js.id).evalmetrics
    print [key for key,value in SAResults.objects.get(job_id=15).final_combined_results.iteritems()]
    pass
