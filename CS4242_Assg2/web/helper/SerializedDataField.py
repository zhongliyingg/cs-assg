'''
Created on 25 Feb, 2014

@author: simkerncheh
'''
'''
Created on Jan 25, 2014

@author: simkerncheh
'''
import base64

from django.db import models


try:
    import cPickle as pickle
except:
    import pickle


class SerializedDataField(models.TextField):
    """Because Django for some reason feels its needed to repeatedly call
    to_python even after it's been converted this does not support strings."""
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value is None: return
        if not isinstance(value, basestring): return value
        value = pickle.loads(base64.b64decode(value))
        return value

    def get_db_prep_save(self, value, connection):
        if value is None: return
        return base64.b64encode(pickle.dumps(value))
