'''
Created on Feb 27, 2014

@author: LIYING
'''
def calculateChi2Values(unique_feat, pos_feat, neg_feat, pos_sample_size, neg_sample_size):
    '''
        Calculate Chi2 values of all unique features using lecture's formula
         
        Params:
            unique_feat: [feat] of unique features
            pos_feat: {feat:count} of positive features
            neg_feat: {feat:count} of negative features
            pos_sample_size: num of positive tweets
            neg_sample_size: num of negative tweets
        Returns:
            chi2_val_list: {feat: chi2_val} of calculated chi2 values
    '''
     
#     print 'using calculateChi2Values...'
    
    chi2_val_list = {}
    for f in unique_feat:
        A = 0
        B = 0
        C = 0
        D = 0
        if f in pos_feat:
            A = pos_feat[f]
        if f in neg_feat:
            B = neg_feat[f]
        C = pos_sample_size - A
        D = neg_sample_size - B
         
#         print A,B,C,D
        chi2_val_num = (A+B+C+D)*(A*D - C*B)*(A*D - C*B)
        chi2_val_denom = (A+C)*(B+D)*(A+B)*(C+D)
         
        if chi2_val_denom == 0:
            chi2_val = 0
        else:
            chi2_val = float(chi2_val_num)/float(chi2_val_denom)
             
        chi2_val_list[f] = chi2_val
 
    return chi2_val_list