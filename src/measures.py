'''MEASURES'''

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import patsy
import dataprep as dp
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr
from sklearn.metrics import r2_score
from functools import partial

# root mean square error (RMSE)
def rmse(pred,true):
	pred=dp.d2s(pred) # DataFrame to Series
	true=dp.d2s(true) # DataFrame to Series
	return np.sqrt(((pred-true) ** 2).mean())

# symmetric mean absolute percentage error
def smape(pred,true):
	pred=dp.d2s(pred) # DataFrame to Series
	true=dp.d2s(true) # DataFrame to Series
	return ((true-pred).abs()/(true.abs()+pred.abs())).mean()

def mase(pred,true,shift=7*24):
	pred=dp.d2s(pred) # DataFrame to Series
	true=dp.d2s(true) # DataFrame to Series
	return ((pred-true)/(true.shift(shift)-true).dropna().abs().mean()).abs().mean()

# finds the best shift to use for naive method and MASE
def opt_shift(data, shifts=[60*24,60*24*7]):
	results=pd.DataFrame() # empty dataframe for scores
	for s1,s2 in [(s1,s2) for s1 in shifts for s2 in shifts]: # for each shift to consider
		measures={'RMSE':rmse,'SMAPE':smape,'MASE':partial(mase,shift=s2)} # measures to consider
		score=acc(pred=data.shift(s1).dropna(), true=data.shift(-s1).dropna()) # compute accuracy measures
		results=pd.concat([results,score]) # append computed measures
	return results

# returns various measures/metrics/scores of goodness of fit 
def acc(pred,true,label='test',measures={'RMSE':rmse,'SMAPE':smape,'MASE':partial(mase,shift=60*24)}):
	score={name:ms(pred=pred,true=true) for name,ms in measures.items()}
	results=pd.DataFrame(data=score,index=[label]) # convert dictionary into a dataframe
	return results


measures={'RMSE':rmse,'SMAPE':smape,'MASE':partial(mase,shift=60*24)}



score={} # initialize dictionary
	score['RMSE']=rmse(pred=pred,true=true) # compute RMSE
	score['SMAPE']=smape(pred=pred,true=true) # compute SMAPE
	score['MASE']=mase(pred=pred,true=true) # compute MASE
