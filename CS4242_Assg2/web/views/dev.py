'''
Created on 26 Feb, 2014

@author: simkerncheh
'''
from CS4242_Assg2.constants import *
from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import HttpResponse
from evaluation.evaluation import verifyGTForClassification, verifyGTForSA
from feature_selection.PolarityScore import loadSWNFromDB
from feature_selection.SentiWordNet import SentiWordNetCorpusReader
from parser2.Parser import getKeyInfoForClassifier, parseLabelFile
from parser2.ParserSA import organizeDataByCategory, getKeyInfoForSA
from web.helper.Jobs_Classifier import performClassification
from web.management.commands.buildslangdict import Command
from web.models import FeatureMatrixClassifier, StorageDict, SAResults
import json
import os.path




def parserresults(request):
    gen = parseLabelFile(PATH_GROUNDTRUTH_TRAINING)
    categories_list = gen['categories']
    groundtruth_list = gen['groundtruth_list']
    r1 = getKeyInfoForClassifier(PATH_TRAINING_DATA, categories_list, groundtruth_list)
    return HttpResponse(json.dumps(r1, cls=DjangoJSONEncoder))

def parserSA(request):
    combined_results = performClassification(PATH_TESTING_DATA, [FEATURE_TEXT, FEATURE_HASHTAG, FEATURE_GEOINFO])
    fm = organizeDataByCategory(PATH_TESTING_DATA, combined_results)
    return HttpResponse(json.dumps(fm, cls=DjangoJSONEncoder))

def classifierresults(request):
    features_used = [FEATURE_TEXT, FEATURE_HASHTAG, FEATURE_GEOINFO]
    combined_results = performClassification(PATH_TESTING_DATA, features_used)
    return HttpResponse(json.dumps(verifyGTForClassification(PATH_GROUNDTRUTH_TESTING, combined_results)))

def sentiwordnet(request):
    if os.path.exists(PATH_SENTIWN):
        swn = SentiWordNetCorpusReader(PATH_SENTIWN)
        swn_map = swn.build_senti_translation_map()
        test = swn_map['v']['do']
        return HttpResponse(json.dumps(test, cls=DjangoJSONEncoder))
    
def sentiwordnetdb(request):
    swn_db = loadSWNFromDB()
    return HttpResponse(json.dumps(swn_db, cls=DjangoJSONEncoder))

def keyinfoSA(request):
    gen = parseLabelFile(PATH_GROUNDTRUTH_TRAINING)
    categories_list = gen['categories']
    groundtruth_list = gen['groundtruth_list']
    results = getKeyInfoForSA(PATH_TRAINING_DATA, categories_list, groundtruth_list)
    return HttpResponse(json.dumps(results, cls=DjangoJSONEncoder))  

def slangdict(request):
    sd = Command().getSlangDict()
    return HttpResponse(json.dumps(sd, cls=DjangoJSONEncoder))

def doa(request):
    dd = StorageDict.objects.get(key=DOA_DICT).stored_dict
    return HttpResponse(json.dumps(dd, cls=DjangoJSONEncoder))

def catresults(request):
    combined_results = performClassification(PATH_TESTING_DATA, FEATURES_DEFAULT)
    return HttpResponse(json.dumps(combined_results, cls=DjangoJSONEncoder))

def emoticons(request):
    dd = StorageDict.objects.get(key=EMOTICONS_DICT).stored_dict
    return HttpResponse(json.dumps(dd, cls=DjangoJSONEncoder))

def evalu(request):
    job_id = request.GET['job_id']
    saresult = SAResults.objects.get(job_id=job_id)
    combined_results = saresult.final_combined_results
    
    evaluation = verifyGTForSA(PATH_GROUNDTRUTH_TESTING, combined_results)
    return HttpResponse(json.dumps(evaluation, cls=DjangoJSONEncoder))
