'''
Created on Feb 28, 2014

@author: LIYING
'''
import codecs

from CS4242_Assg2.constants import *
from CS4242_Assg2.settings import DEBUG_CODE
from console_debug.debug_methods import writeDebugListToFile


def createGroundTruth(labelfile, groundtruth_cat, appendname =''):
    
    if DEBUG_CODE:
        groundtruth_list = []
        with codecs.open(labelfile, encoding='cp1252') as the_file:
            for line in the_file:
                splitarray = line.strip().split(',')
            
                category = splitarray[0][1:-1]
                if category == groundtruth_cat:
                    groundtruth_list.append(1)
                else:
                    groundtruth_list.append(0)
        
#             print groundtruth_list
        writeDebugListToFile("%s_groundtruth_%s.txt"% (groundtruth_cat, appendname), groundtruth_list)

if __name__ == '__main__':
    createGroundTruth(PATH_GROUNDTRUTH_TESTING, "apple", appendname="test")
    createGroundTruth(PATH_GROUNDTRUTH_TESTING, "google", appendname="test")
    createGroundTruth(PATH_GROUNDTRUTH_TESTING, "twitter", appendname="test")
    createGroundTruth(PATH_GROUNDTRUTH_TESTING, "microsoft", appendname="test")
    
    createGroundTruth(PATH_GROUNDTRUTH_TRAINING, "apple", appendname="train")
    createGroundTruth(PATH_GROUNDTRUTH_TRAINING, "google", appendname="train")
    createGroundTruth(PATH_GROUNDTRUTH_TRAINING, "twitter", appendname="train")
    createGroundTruth(PATH_GROUNDTRUTH_TRAINING, "microsoft", appendname="train")
    print "done"
    pass