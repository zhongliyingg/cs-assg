'''
Created on Feb 27, 2014

@author: LIYING
'''
import codecs
import operator
import os

from CS4242_Assg2.constants import *
from CS4242_Assg2.settings import DEBUG_CODE


def debugPrint(print_statement):
    if DEBUG_CODE:
        print print_statement

def printresults(combined_results):
    for category, result in combined_results.iteritems():
        print category
        print "True Positives:" , len(result['true_positive'])
        print "True Negatives:", len(result['true_negative'])
        print "False Positives:", len(result['false_positive'])
        print "False Negatives:", len(result['false_negative'])
        total = len(result['true_positive'])+ len(result['true_negative'])\
                    +len(result['false_positive'])+ len(result['false_negative'])
        print "Total Count:", total
        print "Precision:", result['precision']
        print "Recall:", result['recall']
        print "F1:", result['f_one']

def printresultsSA(combined_results):
    f1_overall = 0.0
    f1_overall_pos = 0.0
    f1_overall_neu = 0.0
    f1_overall_neg = 0.0
    for category, result_set in combined_results.iteritems():
        print category
        f1_category = 0.0    
        for sentiment, result in result_set.iteritems():
            print ">> %s" % sentiment
#             print [k for k in result.iterkeys()]
            print "True Positives:" , len(result['true_positive'])
            print "True Negatives:", len(result['true_negative'])
            print "False Positives:", len(result['false_positive'])
            print "False Negatives:", len(result['false_negative'])
            total = len(result['true_positive'])+ len(result['true_negative'])\
                    +len(result['false_positive'])+ len(result['false_negative'])
            print "Total Count:", total
            print "Precision:", result['precision']
            print "Recall:", result['recall']
            print "F1:", result['f_one']
            f1_category += result['f_one']
            
            if category != NO_CATEGORY:
                if sentiment == POLARITY_POSITIVE:
                    f1_overall_pos += result['f_one']
                if sentiment == POLARITY_NEUTRAL:
                    f1_overall_neu += result['f_one']
                if sentiment == POLARITY_NEGATIVE:
                    f1_overall_neg += result['f_one']
        f1_category_avg = f1_category/3
        print ">> %s F1 average: %s" % (category, f1_category_avg)
        if category != NO_CATEGORY:
            f1_overall += f1_category_avg
            
    fl_overall_avg_pos = f1_overall_pos/(len(combined_results)-1)
    fl_overall_avg_neu = f1_overall_neu/(len(combined_results)-1)
    fl_overall_avg_neg = f1_overall_neg/(len(combined_results)-1)
    f1_overall_avg = f1_overall/(len(combined_results)-1)
    print ">> Overall F1 Positive average: %s" % fl_overall_avg_pos
    print ">> Overall F1 Neutral average: %s" % fl_overall_avg_neu
    print ">> Overall F1 Negative average: %s" % fl_overall_avg_neg
    print ">> Overall F1 average: %s" % f1_overall_avg
        
def writeDebugListToFile(filename, the_list):
    if DEBUG_CODE:
        save_path = PATH_SAVE_DEBUG_FILES+filename
        with codecs.open(save_path, 'w' , encoding='utf-8', errors='replace') as the_file:
            for item in the_list:
                print>>the_file, item
#                 the_file.write("%s\n" % item)

def writeDebugDictToFile(filename, the_dict):
    if DEBUG_CODE:
        save_path = PATH_SAVE_DEBUG_FILES+filename
        with codecs.open(save_path, 'w' , encoding='utf-8', errors='replace') as the_file:
            for key, value in the_dict.iteritems():
                print>>the_file, key, value

def writeDebugCountDictToFile(filename, the_dict):
    if DEBUG_CODE:
        sorted_count_dict = sorted(the_dict.iteritems(),key=operator.itemgetter(1), reverse=True)
        save_path = PATH_SAVE_DEBUG_FILES+filename
        with codecs.open(save_path, 'w' , encoding='utf-8', errors='replace') as the_file:
            for item in sorted_count_dict:
                print>>the_file, item