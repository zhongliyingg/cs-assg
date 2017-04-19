'''
Created on 27 Feb, 2014

@author: simkerncheh
'''
from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from CS4242_Assg2.constants import *

# TODO: Label

#             features_used = [ FEATURE_SA_NEGATION, 
#                  FEATURE_SA_EXCLAMATION_PRESENCE, 
#                  FEATURE_SA_CAPS_PERCENTAGE, FEATURE_SA_CAPS_POLARITY, 
#                  FEATURE_SA_POS, FEATURE_SA_POLARITY_SCORES,
#                  FEATURE_SA_POLARITY_TEXT, FEATURE_SA_POLARITY_POS,  
#                  FEATURE_TEXT, FEATURE_HASHTAG,  
#                  FEATURE_SA_EMOTICONS, FEATURE_SA_EMOTICONS_POLARITY]

SA_OPTIONS = (  (FEATURE_TEXT, 'All Text'),
                (FEATURE_HASHTAG, 'Hashtags'),
                (FEATURE_SA_EMOTICONS, 'Emoticons'),
                
                (FEATURE_SA_POS, 'POS Count'),  
                (FEATURE_SA_NEGATION, 'Negation Word Count'),
                
                (FEATURE_SA_POLARITY_SCORES, 'Polarity Scores'),
                
                (FEATURE_SA_POLARITY_TEXT, 'All Text Polarity Count'),
                (FEATURE_SA_POLARITY_POS, 'POS Polarity Count'),
                (FEATURE_SA_EMOTICONS_POLARITY, 'Emoticons Polarity Count'),
                
                (FEATURE_SA_CAPS_POLARITY, 'Capitalised Text Polarity Count'),
                (FEATURE_SA_CAPS_PERCENTAGE, 'Capitalised Text Percentage'),
                
                (FEATURE_SA_EXCLAMATION_PRESENCE, 'Exclamation Presence'),
                
                (FEATURE_SA_REPLIES, 'User Replies'),
                (FEATURE_SA_TEMPORAL, 'User Replies Temporal')
              )

class UploadTrainingDataForm(forms.Form):
    file_data = forms.FileField(widget=forms.FileInput(attrs={'placeholder': 'Upload File'}))
    file_groundtruth = forms.FileField(widget=forms.FileInput(attrs={'placeholder': 'Upload File'})) 
    options = forms.MultipleChoiceField(widget=CheckboxSelectMultiple, choices=SA_OPTIONS, label='Features:', required=False)
    
class UploadClassificationDataForm(forms.Form):
    file_data = forms.FileField(widget=forms.FileInput(attrs={'placeholder': 'Upload File'}), label='Data File:')
    
class UploadGroundTruthForm(forms.Form):
    job_id = forms.IntegerField(widget=forms.HiddenInput())
    file_groundtruth = forms.FileField(widget=forms.FileInput(attrs={'placeholder': 'Upload File'}), 
                                       label='Groundtruth File', ) 
