'''
Created on 25 Feb, 2014

@author: simkerncheh
'''
from CS4242_Assg2.constants import *
from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from web.form import UploadTrainingDataForm, UploadClassificationDataForm, \
    UploadGroundTruthForm
from web.helper.Jobs_Classifier import performTraining
from web.helper.Jobs_SA import performTrainingForSA, runCategorization, \
    runEvaluation
from web.models import SVMStatesSentimental, JobStatus, SVMStatesClassifier, \
    JobStatusSA, FeatureMatrixClassifier, FeatureMatrixSentimental, SAResults
import codecs
import json
import multiprocessing
import time
'''
Created on 25 Feb, 2014

@author: simkerncheh
'''

def custom_redirect(url_name, *args, **kwargs):
    from django.core.urlresolvers import reverse 
    import urllib
    url = reverse(url_name, args=args)
    params = urllib.urlencode(kwargs)
    
    return HttpResponseRedirect(url + "?%s" % params)

current_milli_time = lambda: int(round(time.time() * 1000))

def analysis(request):
    svmstates = SVMStatesSentimental.objects.all()
    categorylist = [ svm.classifier_name for svm in svmstates ]
    form = UploadClassificationDataForm()
    svmlist = list(SVMStatesSentimental.objects.all())
    newsvmlist = [svm.classifier_name for svm in svmlist ]
    return render(request, 'analysis.html', {'categories': categorylist, 'form': form, 'svmlist': newsvmlist})

def submitanalysis(request):
    
    if request.method == "POST":
        form = UploadClassificationDataForm(request.POST, request.FILES)
        if form.is_valid():
            jobstatus = JobStatus.objects.create()
            
            if request.FILES['file_data'].name.endswith('.txt'):
                data_filename = '%s%s.txt' % (PATH_UPLOAD_TESTING, current_milli_time())
                with codecs.open(data_filename, 'wb+') as destination:
                    for chunk in request.FILES['file_data'].chunks():
                        destination.write(chunk)
        
            if data_filename is not None:
                p = multiprocessing.Process(target=runCategorization, args=(data_filename, jobstatus,))
                p.start()
                return HttpResponse(json.dumps({'type': 'ok', 'message': jobstatus.id}, cls=DjangoJSONEncoder))
            
    return HttpResponse(json.dumps({'type': 'error', 'message': 'Invalid request'}, cls=DjangoJSONEncoder))

def newcategory(request):
    form = UploadTrainingDataForm(initial={'options': FEATURES_SA_DEFAULT})
    return render(request, 'newcategory.html', {'form': form})

def submitcategory(request):
    if request.method == 'POST':
        form = UploadTrainingDataForm(request.POST, request.FILES)
        if form.is_valid():
            
            jobstatus = JobStatus.objects.create()
            jobstatussa = JobStatusSA.objects.create()
            data_filename = None
            label_filename = None
            optionslist = request.POST.getlist('options')
            
            if request.FILES['file_data'].name.endswith('.txt'):
                data_filename = '%s%s.txt' % (PATH_UPLOAD_TRAINING, current_milli_time())
                with codecs.open(data_filename, 'wb+') as destination:
                    for chunk in request.FILES['file_data'].chunks():
                        destination.write(chunk)
                            
            if request.FILES['file_groundtruth'].name.endswith('.txt'):
                label_filename = '%s%s_gt.txt' % (PATH_UPLOAD_TRAINING, current_milli_time())
                with codecs.open(label_filename, 'wb+') as destination:
                    for chunk in request.FILES['file_groundtruth'].chunks():
                        destination.write(chunk)   
                                     
            if data_filename is not None and label_filename is not None:
                p = multiprocessing.Process(target=performTraining, args=(data_filename, label_filename,),
                                            kwargs={'features_used': FEATURES_DEFAULT, 'job_id': jobstatus.id})
                p.start()
                p2 = multiprocessing.Process(target=performTrainingForSA, args=(data_filename, label_filename,),
                                            kwargs={'features_used': optionslist, 'job_id': jobstatussa.id})
                p2.start()
    
                return HttpResponse(json.dumps({'type': 'ok', 'message': jobstatus.id, 'message2': jobstatussa.id }, cls=DjangoJSONEncoder))
            
            else:
                return HttpResponse(json.dumps({'type': 'error', 'message': 'Bad File Type!'}, cls=DjangoJSONEncoder))
#         else:
#             return HttpResponse(json.dumps({'type': 'error', 'message': json.dumps(list(form.errors))}, cls=DjangoJSONEncoder))
        
    return HttpResponse(json.dumps({'type': 'error', 'message': 'Invalid request'}, cls=DjangoJSONEncoder))

def deleteSVM(request):
    if request.method == "GET" and 'svm_name' in request.GET:
        svm_name = request.GET['svm_name']
        FeatureMatrixClassifier.objects.filter(category=svm_name).delete()
        FeatureMatrixSentimental.objects.filter(category=svm_name).delete()
    return analysis(request)


def results(request):
    
    gt = False
    eval_result = []
    svmresults = []
    features_enabled = []
    categorieslist = ['Positive', 'Neutral', 'Negative']
    job_id = -1
    
    if request.method == 'GET' and 'jobid' in request.GET:
        job_id = int(request.GET['jobid'])
        saresult = SAResults.objects.get(job_id=job_id)
        
        if (saresult.evalmetrics is not None):
            gt = True
            eval_result = saresult.evalmetrics
        
        svmresults = saresult.svmresults
        features_enabled =  saresult.features_enabled
        
    
    joblist = list(SAResults.objects.all().order_by('-date').values('job_id', 'date'))
    return render(request, 'results.html', {'joblist': joblist, 'gt': gt, 'eval_result': eval_result,
                                            'svmresults': svmresults, 'features_enabled': features_enabled,
                                            'categorieslist': categorieslist, 'form': UploadGroundTruthForm(initial={'job_id': job_id})})
    
def resultssubmitgt(request):
    if request.method == 'POST':
        form = UploadGroundTruthForm(request.POST, request.FILES)
        if form.is_valid():
            if request.FILES['file_groundtruth'].name.endswith('.txt'):
                gt_filename = '%s_gt_%s.txt' % (PATH_UPLOAD_TRAINING, current_milli_time())
                with codecs.open(gt_filename, 'wb+') as destination:
                    for chunk in request.FILES['file_groundtruth'].chunks():
                        destination.write(chunk)
                job_id = int(form.cleaned_data['job_id'])
                runEvaluation(gt_filename, job_id)
                
                return custom_redirect(results, jobid=job_id)
    return results(request)
