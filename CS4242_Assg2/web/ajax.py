'''
Created on 5 Mar, 2014

@author: simkerncheh
'''
from dajaxice.decorators import dajaxice_register
from django.core.serializers.json import DjangoJSONEncoder
from web.models import JobStatus, JobStatusSA
import json

@dajaxice_register
def getStatus(request, job_id):
    svmstatus = list(JobStatus.objects.filter(id=job_id).values())
    return json.dumps(svmstatus, cls=DjangoJSONEncoder)

@dajaxice_register
def getStatusSA(request, job_id):
    svmstatus = list(JobStatusSA.objects.filter(id=job_id).values())
    return json.dumps(svmstatus, cls=DjangoJSONEncoder)