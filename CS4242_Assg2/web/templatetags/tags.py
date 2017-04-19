'''
Created on 25 Feb, 2014

@author: simkerncheh
'''
from django.template.defaulttags import register
@register.simple_tag
def active(request, pattern):
    import re
    if re.search(pattern, request.path):
        return 'active'
    return ''
