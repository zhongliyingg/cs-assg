'''
Created on Feb 24, 2014

@author: Administrator

Everything is awesome! Everything is cool when you're part of a team!
'''
from CS4242_Assg2.settings import BASE_DIR

# Project specific constants

FEATURE_TEXT = 'text'
FEATURE_HASHTAG = 'hashtags'
FEATURE_USER_MENTIONS = 'user_mentions'

FEATURE_GEOINFO = 'geoinfo'
FEATURE_FOLLOWED_CATEGORIES = 'followed_categories'
FEATURE_USER = 'userid'
# FEATURE_TEMPORAL_INFO = 'temporal_info'
FEATURE_CATEGORY = 'feature_category'


FEATURE_SA_POLARITY_TEXT = "feature_sa_polarity_text"
FEATURE_SA_POLARITY_POS = "feature_sa_polarity_pos"
FEATURE_SA_POS = "feature_sa_pos"
FEATURE_SA_TWEETID_STR = 'tweet_id_str'
FEATURE_SA_REPLY_TO_ID = "feature_sa_reply_to_id"
FEATURE_SA_REPLIES = "feature_sa_replies"
FEATURE_SA_TEMPORAL = 'feature_sa_temporal'

FEATURE_SA_TWITTER_TOKEN_COUNT = "feature_sa_twitter_tokens"

# === Emoticons === #
FEATURE_SA_EMOTICONS = 'feature_sa_emoticons'
FEATURE_SA_EMOTICONS_POLARITY = 'feature_sa_emoticons_polarity'

# === Exclamation === #
FEATURE_SA_EXCLAMATION_PRESENCE = 'feature_sa_exclamation'
FEATURE_SA_EXCLAMATION_COUNT = 'feature_sa_exclamation_count'

# === Negation === #
FEATURE_SA_NEGATION = 'feature_sa_negation'

# === Polarity Scores === #
FEATURE_SA_POLARITY_SCORES = "feature_sa_polarity_scores"

# === Capitalised Text === #
FEATURE_SA_CAPS_PERCENTAGE = 'feature_sa_caps_percentage'
FEATURE_SA_CAPS_POLARITY = 'feature_sa_caps_polarity'  # results will drop
FEATURE_SA_CAPS_PRESENCE = 'feature_sa_caps_presence'

FEATURE_COUNT = 'feature_count'
FEATURE_VALUE = "feature_value"

FEATURES_DEFAULT = [FEATURE_TEXT, FEATURE_HASHTAG, FEATURE_GEOINFO,
                    FEATURE_USER_MENTIONS, FEATURE_CATEGORY]

# FEATURES_SA_DEFAULT = [FEATURE_TEXT, FEATURE_HASHTAG, FEATURE_SA_EMOTICONS, FEATURE_SA_CAPS_POLARITY]
FEATURES_SA_DEFAULT = [ 
                FEATURE_TEXT, FEATURE_HASHTAG, # f1, f2
                FEATURE_SA_EMOTICONS, FEATURE_SA_EMOTICONS_POLARITY, # f3, f9
                FEATURE_SA_NEGATION, # f5  
                FEATURE_SA_POS, FEATURE_SA_POLARITY_POS, #f4, f7
                FEATURE_SA_CAPS_POLARITY, FEATURE_SA_POLARITY_TEXT, #f6, f8
                FEATURE_SA_CAPS_PERCENTAGE, #f11
                FEATURE_SA_POLARITY_SCORES, #f10 
                FEATURE_SA_EXCLAMATION_PRESENCE] #12 
#                 FEATURE_SA_REPLIES, FEATURE_SA_TEMPORAL]

# non-optional feature

FEATURE_CREATED_AT = 'created_at'

# Parser Constants

UNIQUE_FEATURES = 'unique_features'
PROCESSED_TWEETS = 'processed_tweets'

TWEET_ID = 'tweet_id'
TWEET_FULL = 'tweet_full'
TWEET_FEATURES = 'tweet_features'
TWEET_USER_ID = 'user_id'

FEATURES = 'features'

CATEGORY = 'category'
POLARITY = 'polarity'


# File Paths (for development use only!)

PATH_TRAINING_DATA = '%s/dataset/tweets_train.txt' % (BASE_DIR)
PATH_TESTING_DATA = '%s/dataset/tweets_test.txt' % (BASE_DIR)

PATH_GROUNDTRUTH_TRAINING = '%s/dataset/label_train.txt' % (BASE_DIR)
PATH_GROUNDTRUTH_TESTING = '%s/dataset/label_test.txt' % (BASE_DIR)

PATH_UPLOAD_TRAINING = '%s/web/uploads/training/' % (BASE_DIR)
PATH_UPLOAD_TESTING = '%s/web/uploads/testing/' % (BASE_DIR)

PATH_SVM_STATES = '%s/svmstates/' % (BASE_DIR)

PATH_SAVE_DEBUG_FILES = '%s/console_debug/debug_files/' % (BASE_DIR)

#No Category
NO_CATEGORY = 'no_category'

# DOA constants 
DOA_THRES_POLARITY_POS = 1.0-(1.0/6.0)
DOA_THRES_POLARITY_NEG = 0.5
DOA_NO_POLARITY_SCORE = 0

# Polarity constants
POLARITY_WORD = "polarity_word"
POLARITY_SCORES_WORD = "polarity_scores_word"
POLARITY_SCORES_POS = "polarity_scores_pos"

# Classifier constants (for SVM)
POSITIVE = 1
NEGATIVE = 0

POLARITY_POSITIVE = "positive"
POLARITY_NEGATIVE = "negative"
POLARITY_NEUTRAL = "neutral"
POLARITY_NONE = "no_polarity"
POLARITY_VERY_POSITIVE = "very positive"
POLARITY_VERY_NEGATIVE = "very negative"

SVM_X = 'input_matrix'
SVM_Y = 'labels'

TWEET_FEATURE_MATRIX = 'tweet_feature_matrix'
LABEL = 'class'

# Class symbols for SVM
CLASS_SVM_NEGATIVE = "negative"
CLASS_SVM_NEUTRAL = "neutral"
CLASS_SVM_POSITIVE = "positive"

# Ground truth result symbols

RESULT_CORRECT = 2
RESULT_WRONG = 0
RESULT_CLOSE = 1

# SentiWordNet constants
PATH_SENTIWN = '%s/feature_selection/SentiWordNet_3.0.0_20130122.txt' % (BASE_DIR)
TERM_OBJ = 'objectivity'
TERM_POS_SCORE = 'pos_score'
TERM_NEG_SCORE = 'neg_score'

# POS constants
POS_OTHERS = 'others'
POS_NOUN = 'n'
POS_VERB = 'v'
POS_ADJ = 'a'
POS_ADJ_SATELLITE = 's'
POS_ADV = 'r'



# Dictionary of Affect Constants

PATH_DOA = '%s/feature_selection/Dictionary_Of_Affect.txt' % (BASE_DIR)

PLEASANTNESS = 'pleasantness'
ACTIVATION = 'activation'
IMAGERY = 'imagery'

# Emoticon Storage Path

EMOTICONS_DICT = 'emoticons_dict'
PATH_EMOTICONS_DICT = '%s/feature_selection/Emoticons.txt' % (BASE_DIR)
EMOTICON = 'emoticon'
EMOTICON_DESCRIPTION = 'description'
EMOTICON_POLARITY = 'polarity'

# StorageDict Constants

SENTIWORDNET_DICT = 'sentiwordnet_dict'
SLANG_DICT = 'slang_dict'
DOA_DICT = 'doa_dict'

PATH_SLANG_HASHMAP = '%s/feature_selection/SlangMap.txt' % (BASE_DIR)
REMARKS = 'remarks'
ORIG_RESULT = 'original_result'

TEMPORAL_INFO_TIMEFRAME_MINS = 3
