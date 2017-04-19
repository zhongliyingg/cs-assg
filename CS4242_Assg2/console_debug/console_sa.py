# -*- coding: utf-8-*-
'''
Created on Mar 7, 2014

@author: LIYING
'''
import codecs
import string

from CS4242_Assg2.constants import *
from console_debug.debug_methods import printresults, printresultsSA, \
    writeDebugDictToFile
from evaluation.evaluation import verifyGTForClassification, verifyGTForSA
from feature_selection.PolarityScore import mapPennToSentiPOS, \
    getPolarityFromSWN, loadSWNFromDB, loadDOAFromDB, getPolarityScoreFromDOA, \
    getSynonymns
from parser2.ParserSA import *
from parser2.Tokenizer import Tokenizer
from web.helper.DatabaseTools import purgeFeaturesetsFromDB, \
    purgeSVMStatesFromDB, purgeStorageDictFromDB
from web.helper.Jobs_SA import performTrainingForSA, performSA


run_sa = 1
run_train = 1
run_test = 1

run_unit = 0
if __name__ == '__main__':
    
    # WARNING: CANNOT ANYHOW PURGE!
#     purgeStorageDictFromDB()
    tokenizer = Tokenizer(preserve_case=True)
    doa = loadDOAFromDB()
    emo_dict = loadEMODictFromDB()
    sd = loadSlangDict()
   
    if run_unit == 1:
        tweet_text = '@msleamichele @NayaRivera @DiannaAgron @MsAmberPRiley please could u somehow convince #hemo to join #twitter we need her awesomeness!! #glee'
        tweet_text = "this should be a POSITIVE example NO?"
        tweet_text = "#Silver &#GOLD #Apple tumbles no matter how many sold #Microsoft buys them 4 a nice price so get in there show #justsayin #Droid rules inend"
        tweet_text1 = "I have finished the work! lol"
        tweet_text = "This is not a word! Please never get it. i didn't know that"
        tweet_text = "7:^]"
        tweet_text = "lol"
        
#         tweet_text1 = translateSlangs(tweet_text1, sd)
        tokenised_tweet = tokenizer.tokenize(tweet_text1)
#         tokenised_tweet = removeUncapturedTwitterTokens(tokenized_wordlist)
        print tokenised_tweet
        
        negation_info = flagNegatedWords(tokenised_tweet)
#         print negation_info
        pos_tagged_tweet = tagSentiPOS(tokenised_tweet)
        print pos_tagged_tweet
        
        polarity_info = getPolarityInformationOfTweet(pos_tagged_tweet, negation_info[1])
#         print polarity_info
#         print getPolarityScores(pos_tagged_tweet, polarity_info[POLARITY_SCORES_WORD])
        

        cap_text = getCapitalisedText(tokenised_tweet)
#         print cap_text
#         print translateSlangs(tweet_text1, sd)
       
    if run_sa == 1:
        purgeFeaturesetsFromDB()
        purgeSVMStatesFromDB()
        
        if run_train == 1:
            print "TRAINING"
            features_used = [ FEATURE_SA_NEGATION, 
                 FEATURE_SA_EXCLAMATION_PRESENCE, 
                 FEATURE_SA_CAPS_PERCENTAGE, FEATURE_SA_CAPS_POLARITY, 
                 FEATURE_SA_POS, FEATURE_SA_POLARITY_SCORES,
                 FEATURE_SA_POLARITY_TEXT, FEATURE_SA_POLARITY_POS,  
                 FEATURE_TEXT, FEATURE_HASHTAG,  
                 FEATURE_SA_EMOTICONS, FEATURE_SA_EMOTICONS_POLARITY]
#                 FEATURE_SA_REPLIES, FEATURE_SA_TEMPORAL] 

            features_used = FEATURES_SA_DEFAULT
            performTrainingForSA(PATH_TRAINING_DATA, PATH_GROUNDTRUTH_TRAINING, features_used)
        
        if run_train == 1 and run_test == 1:
            print " "
            print "TESTING"
            test_data_list = []
            with codecs.open(PATH_TESTING_DATA, encoding='cp1252') as f:
                for line in f:
                    test_data_list.append(line)
                combined_results = performSA(test_data_list)
                evaluation = verifyGTForSA(PATH_GROUNDTRUTH_TESTING, combined_results, category_evaluation=False)
                printresultsSA(evaluation)
            
            print 'DOA_THRES_POLARITY_POS = %s' % DOA_THRES_POLARITY_POS
            print "DOA_THRES_POLARITY_NEG = %s" % DOA_THRES_POLARITY_NEG
            
            print "FEATURES"
            for feature in features_used:
                print feature
    print 'done'

