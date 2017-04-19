'''
Created on Feb 27, 2014

@author: LIYING
'''
import os

from CS4242_Assg2.constants import SENTIWORDNET_DICT
from CS4242_Assg2.settings import BASE_DIR
from web.models import FeatureMatrixClassifier, FeatureMatrixSentimental, \
    SVMStatesClassifier, SVMStatesSentimental, StorageDict

def purgeStorageDictFromDB():
    StorageDict.objects.all().delete()

def purgeFeaturesetsFromDB():
    FeatureMatrixClassifier.objects.all().delete()
    FeatureMatrixSentimental.objects.all().delete()
#     TemporalInfoCheck.objects.all().delete()
    
def purgeSVMStatesFromDB():
    SVMStatesClassifier.objects.all().delete()
    SVMStatesSentimental.objects.all().delete()
    
    folder = BASE_DIR + '/svmstates'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path) and the_file != '.gitignore':
                os.unlink(file_path)
        except Exception, e:
            print e
            
def updateJobStatus(JobStatus, status):
    JobStatus.status = status
    JobStatus.save()
