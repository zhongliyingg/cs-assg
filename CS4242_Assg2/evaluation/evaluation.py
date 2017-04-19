# -*- coding: cp1252 -*-
'''
Created on Feb 25, 2014

@author: simkerncheh
'''
from CS4242_Assg2.constants import *
from console_debug.debug_methods import writeDebugListToFile
import codecs
import copy

def calculateF1(true_positive, false_positive, false_negative):
    '''
    Calculate precision, recall and F1 values 
    Params:
        true_positive: number of true positives
        false_positive: number of false positives
        false_negative: number of false negatives
    Output:
        tuple
        [0]: precision value
        [1]: recall value
        [2]: F1 value
    '''
    
    if (true_positive + false_positive) == 0:
        precision = 0.0
    else:
        precision = (float(true_positive) / (true_positive + false_positive))
        
    if (true_positive + false_negative) == 0:
        recall = 0.0
    else:   
        recall = (float(true_positive) / (true_positive + false_negative))
        
    if (precision + recall) == 0:
        F_one = 0.0
    else:
        F_one = (2 * precision * recall) / (precision + recall)
    
    return (precision, recall, F_one)

def verifyGTForClassification(groundtruth_filename, combined_results):
    '''
    Testing method
    
    Returns:
        {
            'twitter': {
                'true_positive': [],
                'true_negative': [],
                'false_positive': [],
                'false_negative': []
            },
            ...
        }
    '''
    returnmap = {}
    
    for category in combined_results.iterkeys():
        returnmap[category] = {}
        returnmap[category]['true_positive'] = []
        returnmap[category]['true_negative'] = []
        returnmap[category]['false_positive'] = []
        returnmap[category]['false_negative'] = []
        
    with codecs.open(groundtruth_filename, encoding='cp1252') as f:
        for idx, line in enumerate(f):
            splitarray = line.strip().split(',')
            category = splitarray[0][1:-1]
            tweetid = splitarray[2][1:-1]
            for res_category, resultslist in combined_results.iteritems():
                res = resultslist[idx]
                
                if res == POSITIVE and category == res_category:
                    returnmap[res_category]['true_positive'].append(tweetid)
                elif res == POSITIVE and category != res_category:
                    returnmap[res_category]['false_positive'].append(tweetid)
                elif res == NEGATIVE and category == res_category:
                    returnmap[res_category]['false_negative'].append(tweetid)
                elif res == NEGATIVE and category != res_category:
                    returnmap[res_category]['true_negative'].append(tweetid)
                
                true_positive = len(returnmap[res_category]['true_positive'])
                false_positive = len(returnmap[res_category]['false_positive'])
                false_negative = len(returnmap[res_category]['false_negative'])
                fl_calc = calculateF1(true_positive, false_positive, false_negative)
                
                returnmap[res_category]['precision'] = fl_calc[0]
                returnmap[res_category]['recall'] = fl_calc[1]
                returnmap[res_category]['f_one'] = fl_calc[2]
            
    return returnmap

def verifyGTForSA(groundtruth_filename, combined_results, category_evaluation=True):
    '''
    Testing method
    
    category_evaluation: results only of tweet from category, default True 
    
    combined_results: 
        {
            'twitter': 
            {
                0: [tweet_id]
                1: [1,2,0,1]
            },
            
            'microsoft':{
            ...
            }
        }
    
    Returns:
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
    returnmap = {}
    
    for category in combined_results.iterkeys():
        returnmap[category] = {}
        returnmap[category][CLASS_SVM_NEGATIVE] = {}
        returnmap[category][CLASS_SVM_NEUTRAL] = {}
        returnmap[category][CLASS_SVM_POSITIVE] = {}
        
        for class_svm in returnmap[category].itervalues():
            class_svm['true_positive'] = []
            class_svm['true_negative'] = []
            class_svm['false_positive'] = []
            class_svm['false_negative'] = []
#             class_svm['precision'] = 0
#             class_svm['recall'] = 0
#             class_svm['f_one'] = 0

    groundtruth = {}
    with codecs.open(groundtruth_filename, encoding='cp1252') as f:
        for idx, line in enumerate(f):
            splitarray = line.strip().split(',')
            category = splitarray[0][1:-1]
            sentiment = splitarray[1][1:-1]
            tweetid = splitarray[2][1:-1]
            
            if category not in groundtruth:
                groundtruth[category] = {}
            if category in groundtruth:
                if sentiment not in groundtruth[category]:
                    groundtruth[category][sentiment] = []
                if sentiment in groundtruth[category]:
                    groundtruth[category][sentiment].append(tweetid)    
                    
            if NO_CATEGORY not in groundtruth:
                groundtruth[NO_CATEGORY] = {}
            if NO_CATEGORY in groundtruth:
                if sentiment not in groundtruth[NO_CATEGORY]:
                    groundtruth[NO_CATEGORY][sentiment] = []
                if sentiment in groundtruth[NO_CATEGORY]:
                    groundtruth[NO_CATEGORY][sentiment].append(tweetid) 
                
                    
    for res_category, results in combined_results.iteritems():
        # For each category
        tweet_id_list = results[0]
        tweet_results_list = results[1]
        if res_category not in groundtruth:
            continue # no groundtruth available for category
        
        for sentiment in groundtruth[res_category].iterkeys(): # calc F1 for each sentiment in category
            for idx, res in enumerate(tweet_results_list): # loop through all tweets
                tweet_id_text_map = tweet_id_list[idx]
                tweet_id = str(tweet_id_text_map[TWEET_ID])
                
                if category_evaluation: # results only of tweet from category 
                    gt_cat_senti = groundtruth[NO_CATEGORY][sentiment]
                else:
                    gt_cat_senti = groundtruth[res_category][sentiment]
                      
                    # check if tweet fall under the category
                    not_in_cat = True
                    for cat_senti in groundtruth[res_category].iterkeys():
                        if tweet_id in groundtruth[res_category][cat_senti]:
                            not_in_cat = False
                    if not_in_cat:
                        continue # skip tweet if it doesn't fall under category
                    
                newtweetidtextmap = copy.deepcopy(tweet_id_text_map)
                # Note: Appended by KC for faster processing
                newtweetidtextmap[ORIG_RESULT] = res
                
                
                if res == sentiment and tweet_id in gt_cat_senti:
                    newtweetidtextmap[REMARKS] = "correct"
                    returnmap[res_category][sentiment]['true_positive'].append(newtweetidtextmap)
#                     print "results is %s" % (res), tweet_id_text_map

                elif res == sentiment and tweet_id not in gt_cat_senti:                    
                    newtweetidtextmap[REMARKS] = searchForCorrectSentiment(groundtruth[res_category], tweet_id_text_map[TWEET_ID])
                    returnmap[res_category][sentiment]['false_positive'].append(newtweetidtextmap)
#                     print "result is %s, correct sentiment is %s" % (res, tweet_id_text_map[REMARKS])
#                     print "results is %s" % (res), tweet_id_text_map

                elif res != sentiment and tweet_id in gt_cat_senti:                    
                    newtweetidtextmap[REMARKS] = searchForCorrectSentiment(groundtruth[res_category], tweet_id_text_map[TWEET_ID])
                    returnmap[res_category][sentiment]['false_negative'].append(newtweetidtextmap)
#                     print "result is %s, correct sentiment is %s" % (res, tweet_id_text_map[REMARKS])
#                     print "results is %s" % (res), tweet_id_text_map

                elif res != sentiment and tweet_id not in gt_cat_senti:
                    newtweetidtextmap[REMARKS] = "correct"
                    returnmap[res_category][sentiment]['true_negative'].append(newtweetidtextmap)
#                     print "results is %s" % (res), tweet_id_text_map
                    
            true_positive = len(returnmap[res_category][sentiment]['true_positive'])
            false_positive = len(returnmap[res_category][sentiment]['false_positive'])
            false_negative = len(returnmap[res_category][sentiment]['false_negative'])
            true_negative = len(returnmap[res_category][sentiment]['true_negative'])
            
            fl_calc = calculateF1(true_positive, false_positive, false_negative)
            
            returnmap[res_category][sentiment]['precision'] = fl_calc[0]
            returnmap[res_category][sentiment]['recall'] = fl_calc[1]
            returnmap[res_category][sentiment]['f_one'] = fl_calc[2]
            
    return returnmap

def searchForCorrectSentiment(groundtruth_category, tweetid):
    ret = ""
    for sentiment, ids in groundtruth_category.iteritems():
        if str(tweetid) in ids:
            ret = sentiment
    return ret