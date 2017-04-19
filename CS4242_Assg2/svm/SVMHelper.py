'''
Created on Mar 8, 2014

@author: LIYING
'''

def generateFeatureIds(features, startId):
    id_count = startId
    features_map = {}
    for feature in features:
        features_map[feature] = id_count
        id_count = id_count + 1
    
    return features_map