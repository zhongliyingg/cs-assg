from django.db import models
from web.helper.SerializedDataField import SerializedDataField

# Create your models here.
class FeatureMatrixClassifier(models.Model):
        
    category = models.CharField(primary_key=True, max_length=255)
    feature_to_id_map = SerializedDataField()
    tweet_feature_ids_list = SerializedDataField()
    
    def __unicode__(self):
        return u"category: %s" % (self.category)
    
class FeatureMatrixSentimental(models.Model):
    category = models.CharField(primary_key=True, max_length=255)
    feature_to_id_map = SerializedDataField()
    tweet_feature_matrix_list = SerializedDataField()
    
    def __unicode__(self):
        return u"category: %s" % (self.category)
    
class JobStatus(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=255, blank=True)
    
    def __unicode__(self):
        return u"id: %s" % (self.id)
    
class JobStatusSA(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=255, blank=True)
    
    def __unicode__(self):
        return u"id: %s" % (self.id)
    
class SVMStatesClassifier(models.Model):
    classifier_name = models.CharField(primary_key=True, max_length=255)
    featurematrix = models.ForeignKey(FeatureMatrixClassifier)
    
    state = models.CharField(max_length=255)
    
    def __unicode__(self):
        return u'%s' % (self.classifier_name)
    
class SVMStatesSentimental(models.Model):
    classifier_name = models.CharField(primary_key=True, max_length=255)
    featurematrix = models.ForeignKey(FeatureMatrixSentimental)
    features_enabled = SerializedDataField()  # put in sth like FEATURES_DEFAULT
    
    state = models.CharField(max_length=255)
    
    def __unicode__(self):
        return u'%s' % (self.classifier_name)
    
class StorageDict(models.Model):
    key = models.CharField(primary_key=True, max_length=255)
    stored_dict = SerializedDataField()
    
class SAResults(models.Model):
    job_id = models.IntegerField(primary_key=True)
    date = models.DateTimeField()
    
    features_enabled = SerializedDataField()
    svmresults = SerializedDataField()
    final_combined_results = SerializedDataField()
    evalmetrics = SerializedDataField(null=True, blank=True)

class EmoticonMiningIntermediate(models.Model):
    # For Tagging Use - KC
    emoticon_string = models.CharField(max_length=2048)
    description = models.CharField(max_length=2048, blank=True)
    polarity = models.CharField(max_length=255, blank = True)

class EmoticonMining(models.Model):
    emoticon = models.CharField(max_length=2048)
    description = models.CharField(max_length=2048, blank=True)
    polarity = models.CharField(max_length=255, blank = True)
    
## NO LONGER IN USE
# class TemporalInfo(models.Model):
#     user = models.CharField(max_length=255, primary_key=True)
#     sentiment = models.CharField(max_length=255)
#     last_tweet_time = models.DateTimeField()