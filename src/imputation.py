'''DATA IMPUTATION'''

import numpy as np
import pandas as pd
import dataprep as dp
import performance as pf
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr
from copy import deepcopy
from functools import partial
from tqdm import tqdm

# impute missing values using R
def imp(data,alg,freq=1440,**kwargs):
	data=dp.d2s(data) # convert dataframes to series
	pandas2ri.activate() # activate connection
	ts=ro.r.ts # R time series
	result=pandas2ri.ri2py(alg(ts(ro.FloatVector(data.values),frequency=freq),**kwargs)) # get results of imputation from R
	data=pd.Series(index=data.index,name=data.name,data=np.reshape(result,newshape=data.shape, order='C')) # construct DataFrame using original index and columns
	pandas2ri.deactivate() # deactivate connection
	return data

# returns the longest no outage (LNO)== longest continuous subset with no nan values
def lno(data):	
	u=l=U=L=0 # initial assignment to local & global bounds
	while u<len(data) and l<len(data): # while bounds are within dataframe
		l=u# set the lower bound to the same position as the uper bound
		while (l<len(data) and data.iloc[l]!=data.iloc[l]):l+=1 # while there is nan shift lower bound
		u=l # set the upper bound to the same position as the lower bound
		while (u<len(data) and data.iloc[u]==data.iloc[u]):u+=1 # while there is not a nan shift upper bound
		if (u-l>=U-L):U,L=u,l # if the interval is the longest so far save the corresponding bounds
	return data[L:U] # return LNO
	
# introduce outages to data according to distribution	
def add_out(data,dist):
	prob=np.random.choice(list(dist.keys()),len(data),p=list(dist.values())) # generate lengths of outages
	while True: # while there is no outage
		data_out=deepcopy(data) # copy dataframe to preserve original values
		i=0 # reset start position
		while i<len(data_out): # iterate and add outages
			l=dp.round_u(prob[i]*len(data_out),base=1) # length of outage
			if l>0: # outage occurred
				data_out[i:i+l]=np.nan # introduce new outage of length l
				i+=l # shift current position to the end of outage interval
			else: i+=1 # no outage, next position
		if data_out.isnull().sum()>0: break
	return data_out
	
# count outage lengths
def out_len(data):
	out_len={} # dictionary of outage counts
	out=0 # length of outage
	for i in range(len(data)):
		if data.iloc[i]!=data.iloc[i]: # if nan
			out+=1 # increment current number of consecutive nans
		else: 
			if out in out_len: out_len[out] += 1 # increment dictionary entry
			else: out_len[out] = 1 # new entry in dictionary
			out=0 # reset the number of consecutive nans
	if out in out_len: out_len[out] += 1 # increment dictionary entry
	else: out_len[out] = 1 # new entry in dictionary
	return out_len
	
# returns the distribution outage (consecutive nans) lengths
def out_dist(data):
	out_len=out_len(data)
	out_cnt=sum(out_len.values()) # total number of outages (zero length included)
	out_dist={} # dictionary for outage distribution
	for olen,ocnt in out_len.items(): # for each entry in outage counts
		out_dist[olen/len(data)]=ocnt/out_cnt # transform key and value into fractions
	return out_dist

# returns data imputed with the best method
def opt_imp(data,methods,n_iter=10,freq=1440,measures={'SMAE':pf.smae,'RMSE':pf.rmse,'SRMSE':pf.srmse,'SMAPE':pf.smape,'MASE':partial(pf.mase,shift=60*24*7)}):
	dist=out_dist(data) # get the distribution of outage lengths
	data_lno=lno(data) # get the longest no outage (LNO)
	ts=ro.r.ts # R time series object
	pandas2ri.activate() # activate connection
	results=[] # initialize empty list for results
	for i in range(n_iter): # repeat multiple times becaouse of random nature of outage additions
		data_out=add_out(data=data_lno,dist=dist) # add outages
		data_out_ts=ts(ro.FloatVector(data_out.values),frequency=freq) # construct time series object & estimate frequency
		result=pd.DataFrame() # empty dataframe for scores
		for method in methods: # for each method under consideration
			name=method['name'] # get name
			alg=method['alg'] # get algorithm
			opt=method['opt'] # get options
			for kwargs in dp.dol2lod(opt):	# for all combinations of kwargs
				print(str(i)+':',kwargs) # progress update
				data_imp=pd.Series(index=data_out.index,data=np.reshape(pandas2ri.ri2py(alg(data_out_ts,**kwargs)),newshape=data_out.shape, order='C')) # get results of imputation from R & construct DataFrame using original index and columns
				#data_imp=imp(data=data_out,alg=alg,**kwargs) # impute data with said methods
				label=','.join([name]+[str(key)+':'+str(kwargs[key]) for key in sorted(kwargs)]) # build entry label from sorted keys
				pfm=pf.ev(pred=data_imp,true=data_lno,label=label,measures=measures) # evaluate performance
				result=pd.concat([result,pfm]) # append computed performance
		result.index.name='method' # name index column
		results.append(result) # add to results
	pandas2ri.deactivate() # deactivate connection
	return sum(results)/n_iter

