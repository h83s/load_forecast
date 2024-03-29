'''
Created on 4 Dec 2016

@author: SABA
'''
import os
import numpy as np
import sklearn
import matplotlib.pyplot as plt
import pandas as pd


#from numpy.distutils.conv_template import file
#from pandas.io.tests.parser import parse_dates


# PARAMETERS

time_ints=24 # number of time intervals
cols=np.arange(1,1+time_ints).tolist() # column names


# LOADING ENVIRONMENTAL DATA
dir_data='C:/Users/SABA/Google Drive/mtsg/data/homeB-all/homeB-environmental/'

temp_in = pd.DataFrame(columns=cols) # inside temperature
temp_out = pd.DataFrame(columns=cols) # outside temperature
hum_in = pd.DataFrame(columns=cols) # inside humidity
hum_out = pd.DataFrame(columns=cols) # outside humidity

for file in os.listdir(dir_data):
	if file.endswith(".csv"):
		env_raw =pd.read_csv(r'C:\Users\SABA\Google Drive\mtsg\data\homeB-all\homeB-power\2012-Apr-15.csv',header=None,sep=",",usecols=[0,1,2,3,4], names=['timestamp','temp_in','temp_out','hum_in','hum_out'],index_col=[0]) # load loads
		# add previous values for missing timestamps
		# maybe predict them from a couple of previus values?
		start=env_raw.index.min() # first value of new index
		idx=pd.Index(np.arange(start=start,stop=start+60*60*24,step=300)) # timestamps for the whole day, end at 23:59:59
		env_full=env_raw.reindex(idx, method='nearest') # fill missing with nearest values (predict them?)
		temp_in_hrs=load_full.as_matrix(columns=['temp_in']).reshape(-1,load_full.shape[0]//time_ints).average(axis=1) # averaging inside temperature
		temp_out_hrs=load_full.as_matrix(columns=['temp_out']).reshape(-1,load_full.shape[0]//time_ints).average(axis=1) # averaging outside temperature
		hum_in_hrs=load_full.as_matrix(columns=['hum_in']).reshape(-1,load_full.shape[0]//time_ints).average(axis=1) # averaging inside humidity
		hum_out_hrs=load_full.as_matrix(columns=['hum_out']).reshape(-1,load_full.shape[0]//time_ints).average(axis=1) # averaging outside humidity
		temp_in.loc[temp_in.shape[0]]=temp_in_hrs
		temp_out.loc[temp_out.shape[0]]=temp_out_hrs
		hum_in.loc[hum_in.shape[0]]=hum_in_hrs
		hum_out.loc[hum_out.shape[0]]=hum_out_hrs



plt.plot(loads.loc[80])
plt.show()

# MISSING DATA HISTOGRAM 

dir_data='C:/Users/SABA/Google Drive/mtsg/data/homeB-all/homeB-power/'
#loads_all = pd.DataFrame(columns=['time','load'])
loads_list=[]

for file in os.listdir(dir_data):
	if file.endswith(".csv"):
		load_raw =pd.read_csv(dir_data+file,header=None,sep=",",usecols=[0,1], parse_dates=True, names=['time','load'],index_col=[0]) # load loads
		loads_list.append(load_raw)
		
loads_all=pd.concat(loads_list)		


# LOADING LOAD DATA
dir_data='C:/Users/SABA/Google Drive/mtsg/data/homeB-all/homeB-power/'
loads = pd.DataFrame()

for file in os.listdir(dir_data):
	if file.endswith(".csv"):
		load_raw =pd.read_csv(dir_data+file,header=None,sep=",",usecols=[0,1], parse_dates=True, date_parser=(lambda x:pd.to_datetime(x,unit='s')), names=['time','load'],index_col=[0]) # load loads
		if load_raw.shape[0]/(60*60*24)<0.90: # discard file with more than 5% missing data
			continue
		# add previous values for missing timestamps
		# maybe predict them from a couple of previus values?
		start=load_raw.index.min() # first value of new index
		idx=pd.date_range(start=start,periods=86400,freq='1S') # timestamps for the whole day, end at 23:59:59
		load_full=load_raw.reindex(idx, method='nearest') # fill missing with nearest values (predict them?)
		load_hrs=load_full.resample('H').sum() # hourly aggregation of loads
		# build new entry for current day
		load_hrs['date']=pd.DatetimeIndex(load_hrs.index).date # new index
		load_hrs['time']=pd.DatetimeIndex(load_hrs.index).time # new columns
		loads=loads.append(load_hrs.pivot(index='date', columns='time', values='load')) # pivot & append new entry

loads.ix['2012-06-04'].plot(y='load')

plt.plot(np.arange(24),loads.ix[19].values[1:])
plt.plot(np.arange(24),load_hrs.tolist())
plt.show() 

# DATA PROCESSING METHODS

# loads data
def load_data(path='C:/Users/SABA/Google Drive/mtsg/data/household_power_consumption.csv'):
	load=pd.read_csv(path,header=0,sep=";",usecols=[0,1,2], names=['date','time','load'],dtype={'load': np.float64},na_values=['?'], parse_dates=['date'], date_parser=(lambda x:pd.to_datetime(x,format='%d/%m/%Y'))) # read csv
	load['hour']=pd.DatetimeIndex(load['time']).hour # new culumn for hours
	load['minute']=pd.DatetimeIndex(load['time']).minute # new column for minutes
	load=pd.pivot_table(load,index=['date','hour'], columns='minute', values='load') # pivot so that minutes are columns, date & hour multi-index and load is value
	load=load.applymap(lambda x:(x*1000)/60) # convert kW to Wh 
	load.sort_index(inplace=True) # sort entries (just in case)
	return load

# remove incomplete first and last days
def cut_data(data_temp,inplace=False):
	if (inplace):data=data_temp
	else: data=data_temp.copy()
	f,_=data.index.min() # first day
	l,_=data.index.max() # last day
	if (len(data.loc[f])<24): # if first day is incomplete
		data.drop(f,level=0,inplace=True) # drop the whole day
	if (len(data.loc[l])<24): # if last day is incomplete
		data.drop(l,level=0,inplace=True) # drop the whole day
	return data

# loads generator data
def load_gen_data(path='C:/Users/SABA/Google Drive/mtsg/code/generator/out/Electricity_Profile.csv'):
	load_raw =pd.read_csv(path,header=None,sep=",",usecols=[0], names=['load'],dtype={'load': np.float64}) # load loads
	load=load_raw.groupby(load_raw.index//60).sum() # hourly aggregation
	nb_days=load.shape[0]//24 # number of days
	load['hour']=pd.Series(np.concatenate([np.arange(1,25)]*nb_days)) # new column for pivoting
	load['day']=pd.Series(np.repeat(np.arange(1,nb_days+1), repeats=24)) # new column for pivoting
	load=load.pivot(index='day',columns='hour',values='load') # pivoting
	return load

# shifts data for time series forcasting
def shift_data(data,nb_shifts=1,shift=7):
	data_lagged={} # lagged dataframes for merging
	for i in range(0,nb_shifts+1): # for each time step
		data_lagged[i-nb_shifts]=data.shift(-i*shift) # add lagged dataframe
	res=pd.concat(data_lagged.values(),axis=1,join='inner',keys=data_lagged.keys()) # merge lagged dataframes	
	return res.dropna()

# separates data into training & testing sets & converts dataframes to numpy matrices 
def format_data(path='C:/Users/SABA/Google Drive/mtsg/code/generator/out/Electricity_Profile.csv', lag=1, test_size=0.2):
	data=shift_data(load_data(path),nb_shifts=lag)
	train, test =split_train_test(data, test_size)
	X_train,Y_train=split_X_Y(train)
	X_test,Y_test=split_X_Y(test)
	return X_train.as_matrix(), Y_train.as_matrix(), X_test.as_matrix(), Y_test.as_matrix()

# split data into X & Y
def split_X_Y(data):
	X=data.select(lambda x:x[0] not in [0], axis=1)
	Y=data[0]
	return X, Y

# split data into train & test sets
def split_train_test(data, test_size=0.2):
	from sklearn.model_selection import train_test_split
	train, test =train_test_split(data, test_size=test_size)
	return train,test

# split data into 7 datasets according to weekdays
def split_week_days(data):
	Sun=data.iloc[::7, :] # simulation starts on Sunday 1 of January
	Mon=data.iloc[1::7, :]
	Tue=data.iloc[2::7, :]
	Wen=data.iloc[3::7, :]
	Thu=data.iloc[4::7, :]
	Fri=data.iloc[5::7, :]
	Sat=data.iloc[6::7, :]
	return Sun, Mon, Tue, Wen, Thu, Fri, Sat
	
# create & train basic NN model
def create_model(nb_in=24, nb_out=24, nb_hidden=50, nb_epoch=200, batch_size=1, activation='relu', loss='mean_squared_error', optimizer='adam'):
	from keras.models import Sequential
	from keras.layers.core import Dense
	model = Sequential() # FFN
	model.add(Dense(nb_hidden, input_dim=nb_in,activation=activation)) # input & hidden layers
	#model.add(Dropout({{uniform(0, 1)}})) # randomly set a number of inputs to 0 to prevent overfitting
	model.add(Dense(nb_out)) # output layer
	model.compile(loss=loss, optimizer=optimizer) # assemble network	
	return model

# missing data statistics

# plot histogram of missing data
def nan_hist(data):
	import matplotlib.pyplot as plt
	nans=data.isnull().sum(axis=1) # count NaNs row-wise
	_,ax = plt.subplots() # get axis handle
	ax.set_yscale('log') # set logarithmic scale for y-values
	nans.hist(ax=ax,bins=60,bottom=1) # plot histogram of missing values, 
	plt.show()

# plot heatmap of missing data
def nan_heat(data):
	import matplotlib.pyplot as plt
	import seaborn as sns
	nans=data.isnull().sum(axis=1).unstack(fill_value=60) # count NaNs for each hour & 
	sns.heatmap(nans) # produce heatmap

# plot bars  for missing data
def nan_bar(data):
	import matplotlib.pyplot as plt
	nans=data.isnull().sum(axis=1) # count NaNs row-wise
	nans.plot(kind='bar') # plot histogram of missing values,

# generator data
# mlp optimisation
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPRegressor

seed=0 # fix seed for reprodicibility
np.random.seed(seed)
path='C:/Users/SABA/Google Drive/mtsg/code/generator/out/Electricity_Profile.csv' # data path
model=MLPRegressor(solver='adam') # configure model
# grid parameter space
param_grid={'hidden_layer_sizes': [(10,), (25,), (50,), (75,),(100,),(125,),(150,)],
		'max_iter': [1000],
		'batch_size':[1,10,20,50,100,200]
		}

for i in range(1,6): # optimize number of time steps
	Sun,Mon,Tue,Wen,Thu,Fri,Sat=split_week_days(load_data(path))
	X,Y=split_X_Y(shift_data(Wen,nb_shifts=i,shift=1)) # prepare data
	best_model = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1) # configure grid search
	search_result = best_model.fit(X.as_matrix(), Y.as_matrix())
	print("Best: %f using %s" % (search_result.best_score_, search_result.best_params_))
	means = search_result.cv_results_['mean_test_score']
	stds = search_result.cv_results_['std_test_score']
	params = search_result.cv_results_['params']
	for mean, stdev, param in zip(means, stds, params):
		print("%f (%f) with: %r" % (mean, stdev, param))
	print()


# French data optimisation
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPRegressor

seed=0 # fix seed for reprodicibility
np.random.seed(seed)
path='C:/Users/SABA/Google Drive/mtsg/data/household_power_consumption.csv' # data path

load=load_data(path) # load data
nan_hist(load)
nan_bar(load)
nan_heat(load)

# keep NANs
load_with_nans=load.apply(axis=1,func=(lambda x: np.nan if (x.isnull().sum()>0) else x.sum())).unstack() # custom sum function where any Nan in arguments gives Nan as result
#load_with_nans.isnull().equals(load.isnull().any(axis=1)) # check correctness of lambda function

model=MLPRegressor(solver='adam') # configure model
# grid parameter space
param_grid={'hidden_layer_sizes': [(10,), (25,), (50,), (75,),(100,),(125,),(150,)],
		'max_iter': [1000],
		'batch_size':[1,10,20,50,100,200]
		}

for i in range(1,6): # optimize number of time steps
	X,Y=split_X_Y(shift_data(load_with_nans,nb_shifts=i,shift=1).dropna()) # prepare data
	best_model = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1) # setting up grid search
	search_result = best_model.fit(X.as_matrix(), Y.as_matrix()) #  find best parameters
	print("Best: %f using %s" % (search_result.best_score_, search_result.best_params_))
	means = search_result.cv_results_['mean_test_score']
	stds = search_result.cv_results_['std_test_score']
	params = search_result.cv_results_['params']
	for mean, stdev, param in zip(means, stds, params):
		print("%f (%f) with: %r" % (mean, stdev, param))
	print()


# recurrent network optimisation

from tensorflow.contrib.learn import

import tensorflow.contrib.learn.python.learn as learn
from sklearn import datasets, metrics
from sklearn.model_selection import GridSearchCV

iris = datasets.load_iris()
feature_columns = learn.infer_real_valued_columns_from_input(iris.data)
classifier = learn.DNNClassifier(hidden_units=[10, 20, 10], n_classes=3, feature_columns=feature_columns)

param_grid={'steps': [1000],
		'batch_size':[1,10,20,50,100,200]
		}

best_model = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1) # setting up grid search
search_result = best_model.fit(X.as_matrix(), Y.as_matrix()) #  find best parameters



classifier.fit(iris.data, iris.target, steps=200, batch_size=32)
iris_predictions = list(classifier.predict(iris.data, as_iterable=True))
score = metrics.accuracy_score(iris.target, iris_predictions)
print("Accuracy: %f" % score)








classifier.fit(training_set.data,training_set.target)


# Evaluate accuracy.
accuracy_score = classifier.evaluate(x=test_set.data,
									 y=test_set.target)["accuracy"]
print('Accuracy: {0:f}'.format(accuracy_score))

# Classify two new flower samples.
new_samples = np.array(
	[[6.4, 3.2, 4.5, 1.5], [5.8, 3.1, 5.0, 1.7]], dtype=float)
y = list(classifier.predict(new_samples, as_iterable=True))
print('Predictions: {}'.format(str(y)))





























from sklearn.metrics import mean_squared_error, make_scorer
from keras.wrappers.scikit_learn import KerasClassifier
model = KerasClassifier(build_fn=create_model)
mse = make_scorer(mean_squared_error, multioutput='uniform_average')

#nb_hidden=[10,20,30,40,50,60,70,80,90,100] # domain for number of hidden neurons
nb_in=[X.shape[1]]
nb_out=[Y.shape[1]]
nb_hidden=[10,20,30]
param_grid={'nb_hidden':nb_hidden} # grid parameter space
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1, scoring='r2')
grid_result = grid.fit(X.as_matrix(), Y.as_matrix())
# summarize results




model=create_model(X_train.shape[1],Y_train.shape[1])
model.fit(X_train, Y_train, batch_size=batch_size, nb_epoch=nb_epoch, verbose=2)
data_pred=model.predict(X_test)

plt.plot(data_pred[0])
plt.plot(Y_test[0])
plt.show()



# Use scikit-learn to grid search the number of neurons
import numpy
from sklearn.model_selection import GridSearchCV
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.wrappers.scikit_learn import KerasClassifier
from keras.constraints import maxnorm
# Function to create model, required for KerasClassifier
def create_model(neurons=1):
	# create model
	model = Sequential()
	model.add(Dense(neurons, input_dim=8, init='uniform', activation='linear', W_constraint=maxnorm(4)))
	model.add(Dropout(0.2))
	model.add(Dense(1, init='uniform', activation='sigmoid'))
	# Compile model
	model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
	return model
# fix random seed for reproducibility
seed = 7
np.random.seed(seed)
# load dataset
dataset = np.loadtxt('C:/Users/SABA/Google Drive/mtsg/code/load_forecast/src/models/pima-indians-diabetes.csv', delimiter=",")
# split into input (X) and output (Y) variables
X = dataset[:,0:8]
Y = dataset[:,8]
# create model
model = KerasClassifier(build_fn=create_model, nb_epoch=100, batch_size=10, verbose=0)
# define the grid search parameters
neurons = [1, 5, 10, 15, 20, 25, 30]
param_grid = dict(neurons=neurons)
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1)
grid_result = grid.fit(X, Y)
# summarize results
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
	print("%f (%f) with: %r" % (mean, stdev, param))



from hyperopt import Trials, STATUS_OK, tpe
from hyperas import optim


for l in range(1,3):
	best_run, best_model = optim.minimize(model=model,
										  data=data(l),
										  algo=tpe.suggest,
										  max_evals=5,
										  trials=Trials())
	X_train, Y_train, X_test, Y_test = data()
	print("Evalutation of best performing model:")
	print(best_model.evaluate(X_test, Y_test))







	









def cut_data(data,steps=1):
	new_dict={}
	tuples=[] # multiIndex
	for col in data:
		new_dict[col]=data[col] # add old column
		for i in range(1,steps+1):
			new_dict['%s_lag%d' %(col,i)]=data[col].shift(i) # add shifted column
			tuples.append((i,col)) # new multiIndex entry 
	res=pd.DataFrame(new_dict,index=data.index) 
	return res.dropna(axis=0)
	
	
	
measures={'SRMSE':pf.srmse} # performance to consider	
pred = pd.DataFrame({'A': list(range(5))*3,'B': list(range(5))*3,'C': list(range(5))*3,'D': list(range(5))*3})
new=pd.DataFrame({'A': [1.5],'B': [2.5],'C': [3.5],'D': [1.5]})
pred=pd.concat([pred,new]).reset_index(drop=True)


true = pd.DataFrame({'A': [1]*16,'B': [2]*16,'C': [3]*16,'D': [1]*16})

df2 = pd.DataFrame({'A': ['A4', 'A5', 'A6', 'A7'],'B': ['B4', 'B5', 'B6', 'B7'],'C': ['C4', 'C5', 'C6', 'C7'],'D': ['D4', 'D5', 'D6', 'D7']},index=[4, 5, 6, 7])

df = pd.DataFrame({'A': [0,1,2,3],'B': [4,5,6,7],'C': [8,9,10,11],'D': [12,13,14,15]})


df=pd.Series(range(1000))

	
	for col in data:
		new_dict[col]=data[col] # add old column
		for i in range(1,steps+1):
			new_dict['%s_lag%d' %(col,i)]=data[col].shift(i) # add shifted column 
	res=pd.DataFrame(new_dict,index=data.index) 
	return res.dropna(axis=0)




load.plot(kind='bar')




dir_data='C:/Users/SABA/Google Drive/mtsg/data/homeB-all/homeB-power/'
loads = pd.DataFrame(columns=['day'] + cols)

for file in os.listdir(dir_data):
	if file.endswith(".csv"):
		load_raw =pd.read_csv(dir_data+file,header=None,sep=",",usecols=[0,1], parse_dates=True, date_parser=(lambda x:pd.to_datetime(x,unit='s')), names=['time','load'],index_col=[0]) # load loads
		if load_raw.shape[0]/(60*60*24)<0.90: # discard file with more than 5% missing data
			continue
		# add previous values for missing timestamps
		# maybe predict them from a couple of previus values?
		start=load_raw.index.min() # first value of new index
		idx=pd.date_range(start=start,periods=86400,freq='1S') # timestamps for the whole day, end at 23:59:59
		#idx=pd.Index(np.arange(start,start+60*60*24)) # timestamps for the whole day, end at 23:59:59
		load_full=load_raw.reindex(idx, method='nearest') # fill missing with nearest values (predict them?)
		load_full.resample('H').sum() # aggregate hours
		#load_hrs=load_full.as_matrix(columns=['load']).reshape(-1,load_full.shape[0]//time_ints).sum(axis=1) # aggregation for time intervals
		pd.concat(loads,)
		loads.loc[loads.shape[0]]=[start]+load_hrs.tolist()

loads.set_index('day', inplace=True)

 
 
 
 
 
load_dh=np.reshape(load_h,(365,-1),order='C')

X=np.arange(0,np.size(load_dh, axis=0))


seed=0
np.random.seed(seed)


#create model
print('creating model')

model = Sequential()
model.add(Dense(100, input_dim=1, init='uniform', activation='relu'))
model.add(Dense(24, init='uniform', activation='sigmoid'))
model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mean_squared_error'])

# training
print('Training')

model.fit(X, load_dh, batch_size=10, nb_epoch=10000, verbose=2, validation_split=0.3, shuffle=True)

scores = model.evaluate(X, load_dh)
print("%s: %.2f%%" % (model.metrics_names[1], scores[1]))



# Multilayer Perceptron to Predict International Airline Passengers (t+1, given t, t-1, t-2)
import numpy
import matplotlib.pyplot as plt
import pandas
import math
from keras.models import Sequential
from keras.layers import Dense
# convert an array of values into a dataset matrix
def create_dataset(dataset, look_back=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back-1):
		a = dataset[i:(i+look_back), 0]
		dataX.append(a)
		dataY.append(dataset[i + look_back, 0])
	return numpy.array(dataX), numpy.array(dataY)
# fix random seed for reproducibility
numpy.random.seed(7)
# load the dataset
dataframe = pd.read_csv('C:/Users/SABA/Google Drive/mtsg/code/load_forecast/src/models/international-airline-passengers.csv', usecols=[1], engine='python', skipfooter=3)
dataset = dataframe.values
dataset = dataset.astype('float32')
# split into train and test sets
train_size = int(len(dataset) * 0.67)
test_size = len(dataset) - train_size
train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:]
print(len(train), len(test))
# reshape dataset
look_back = 10
trainX, trainY = create_dataset(train, look_back)
testX, testY = create_dataset(test, look_back)
# create and fit Multilayer Perceptron model
model = Sequential()
model.add(Dense(8, input_dim=look_back, activation='relu'))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(trainX, trainY, nb_epoch=200, batch_size=2, verbose=2)
# Estimate model performance
trainScore = model.evaluate(trainX, trainY, verbose=0)
print('Train Score: %.2f MSE (%.2f RMSE)' % (trainScore, math.sqrt(trainScore)))
testScore = model.evaluate(testX, testY, verbose=0)
print('Test Score: %.2f MSE (%.2f RMSE)' % (testScore, math.sqrt(testScore)))
# generate predictions for training
trainPredict = model.predict(trainX)
testPredict = model.predict(testX)
# shift train predictions for plotting
trainPredictPlot = numpy.empty_like(dataset)
trainPredictPlot[:, :] = numpy.nan
trainPredictPlot[look_back:len(trainPredict)+look_back, :] = trainPredict
# shift test predictions for plotting
testPredictPlot = numpy.empty_like(dataset)
testPredictPlot[:, :] = numpy.nan
testPredictPlot[len(trainPredict)+(look_back*2)+1:len(dataset)-1, :] = testPredict
# plot baseline and predictions
plt.plot(dataset)
plt.plot(trainPredictPlot)
plt.plot(testPredictPlot)
plt.show()







# Use scikit-learn to grid search the batch size and epochs
import numpy
from sklearn.model_selection import GridSearchCV
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
# Function to create model, required for KerasClassifier
def create_model():
	# create model
	model = Sequential()
	model.add(Dense(12, input_dim=8, activation='relu'))
	model.add(Dense(1, activation='sigmoid'))
	# Compile model
	model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
	return model
# fix random seed for reproducibility
seed = 7
numpy.random.seed(seed)
# load dataset
dataset = numpy.loadtxt("C:/Users/SABA/Google Drive/mtsg/code/load_forecast/src/models/pima-indians-diabetes.csv", delimiter=",")
# split into input (X) and output (Y) variables
X = dataset[:,0:8]
Y = dataset[:,8]
# create model
model = KerasClassifier(build_fn=create_model, verbose=0)
# define the grid search parameters
batch_size = [10, 20, 40, 60, 80, 100]
epochs = [10, 50, 100]
param_grid = dict(batch_size=batch_size, nb_epoch=epochs)
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=-1)
grid_result = grid.fit(X, Y)
# summarize results
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))














impts=importr('imputeTS') # package for time series imputation

random={}
mean={'option':['mean','median','mode']} # params for mean
ma={'weighting':['simple','linear','exponential'],'k':np.arange(2,11)} # params for moving average
locf={'option':['locf','nocb'],'na_remaining':['rev']} # params for last observation carry forward
interpol={'option':['linear','spline','stine']} # params for interpolation
kalman={'model':['auto.arima','structTS']}

methods=[{'name':'random','alg':impts.na_random,'opt':random},
		{'name':'mean','alg':impts.na_mean,'opt':mean},
		{'name':'ma','alg':impts.na_ma,'opt':ma},
		{'name':'locf','alg':impts.na_locf,'opt':locf},
		{'name':'interpol','alg':impts.na_interpolation,'opt':interpol},
		{'name':'kalman','alg':impts.na_kalman,'opt':kalman},
		{'name':'seadec','alg':impts.na_seadec,'opt':{'algorithm':{'random':random,'mean':mean,'ma':ma,'locf':locf,'interpolation':interpol,'kalman':kalman}}},
		{'name':'seasplit','alg':impts.na_seasplit,'opt':{'algorithm':{'random':random,'mean':mean,'ma':ma,'locf':locf,'interpolation':interpol,'kalman':kalman}}}]


methods={impts.na_random:random,
		impts.na_mean:mean,
		impts.na_ma:ma,
		impts.na_locf:locf,
		impts.na_interpolation:interpol,
		impts.na_kalman:kalman,
		impts.na_seadec:{'algorithm':{'random':random,'mean':mean,'ma':ma,'locf':locf,'interpolation':interpol,'kalman':kalman}},
		impts.na_seasplit:{'algorithm':{'random':random,'mean':mean,'ma':ma,'locf':locf,'interpolation':interpol,'kalman':kalman}}}




for method,params in methods.items():
	for kwargs in [{kw:arg for kw,arg in comb} for comb in product(*[[(kw,arg) for arg in args] for kw,args in params.items()])]: # for all combinations of kwargs
		print(kwargs)
		#data_imp=imp(data=data_out,method=method,**kwargs)
	




for kwargs in [{kw:arg for kw,arg in comb}for comb in product(*[[(kw,arg) for arg in args] for kw,args in params.items()])]: print(kwargs)
	
	
[[[(kw,k) for k,a in dict.items()] for dict in args] for kw,args in params.items()]
	
	# TODO: make [**kwargs] for all combination in params
	kwargs=[{kw:arg for kw,arg in params.items()}]
	{ for in product(params.values())}
	print(kwargs)
	# if element of params is dictionary, extract & combine contents
	# method(params)

for tuple in product(*[[(kw,arg) for arg in args] for kw,args in params.items()]):
		d={k:a for k,a in tuple}
		print(d)
	
if method=='random':
		result=pandas2ri.ri2py(impts.na_random(ro.FloatVector(data.values)) # get results of imputation from R
	if method=='mean':
		result=pandas2ri.ri2py(impts.na_mean(ro.FloatVector(data.values),option='mean')) # get results of imputation from R
	if method=='median':
		result=pandas2ri.ri2py(impts.na_mean(ro.FloatVector(data.values),option='median')) # get results of imputation from R
	if method=='mode':
		result=pandas2ri.ri2py(impts.na_mean(ro.FloatVector(data.values),option='mode')) # get results of imputation from R
	if method=='ma_simple':
		result=pandas2ri.ri2py(impts.na_ma(ro.FloatVector(data.values),weighting='simple')) # get results of imputation from R
	if method=='ma_lin':
		result=pandas2ri.ri2py(impts.na_ma(ro.FloatVector(data.values),weighting='linear')) # get results of imputation from R
	if method=='ma_exp':
		result=pandas2ri.ri2py(impts.na_ma(ro.FloatVector(data.values),weighting='exponential')) # get results of imputation from R
	if method=='locf':
		result=pandas2ri.ri2py(impts.na_locf(ro.FloatVector(data.values),option='locf',na_remaining='rev')) # get results of imputation from R
	if method=='nocb':
		result=pandas2ri.ri2py(impts.na_locf(ro.FloatVector(data.values),option='nocb',na_remaining='rev')) # get results of imputation from R
	if method=='interpol_lin':
		result=pandas2ri.ri2py(impts.na_interpolation(ro.FloatVector(data.values),option='linear') # get results of imputation from R
	if method=='interpol_spline':
		result=pandas2ri.ri2py(impts.na_interpolation(ro.FloatVector(data.values),option='spline') # get results of imputation from R
	if method=='interpol_stine':
		result=pandas2ri.ri2py(impts.na_interpolation(ro.FloatVector(data.values),option='stine') # get results of imputation from R
	if method=='seadec_interpol':
		result=pandas2ri.ri2py(impts.na_seadec(ro.FloatVector(data.values),algorithm='interpolation')) # get results of imputation from R
	if method=='seadec_locf':
		result=pandas2ri.ri2py(impts.na_seadec(ro.FloatVector(data.values),algorithm='locf')) # get results of imputation from R
	if method=='seadec_mean':
		result=pandas2ri.ri2py(impts.na_seadec(ro.FloatVector(data.values),algorithm='mean',option='mean')) # get results of imputation from R
	if method=='seadec_median':
		result=pandas2ri.ri2py(impts.na_seadec(ro.FloatVector(data.values),algorithm='mean',option='median')) # get results of imputation from R
	if method=='seadec_mode':
		result=pandas2ri.ri2py(impts.na_seadec(ro.FloatVector(data.values),algorithm='mean',option='mode')) # get results of imputation from R
	if method=='seadec_random':
		result=pandas2ri.ri2py(impts.na_seadec(ro.FloatVector(data.values),algorithm='random')) # get results of imputation from R
	if method=='seadec_kalman':
		result=pandas2ri.ri2py(impts.na_seadec(ro.FloatVector(data.values),algorithm='kalman')) # get results of imputation from R
	if method=='seadec_ma':
		result=pandas2ri.ri2py(impts.na_seadec(ro.FloatVector(data.values),algorithm='ma')) # get results of imputation from R
	if method=='kalman_arima':
		result=pandas2ri.ri2py(impts.na_kalman(ro.FloatVector(data.values),model='auto.arima')) # get results of imputation from R
	if method=='kalman_structTS':
		result=pandas2ri.ri2py(impts.na_kalman(ro.FloatVector(data.values),model='structTS')) # get results of imputation from R
	if method=='seasplit_interpol':
		result=pandas2ri.ri2py(impts.na_seasplit(ro.FloatVector(data.values),algorithm='interpolation')) # get results of imputation from R
	if method=='seasplit_locf':
		result=pandas2ri.ri2py(impts.na_seasplit(ro.FloatVector(data.values),algorithm='locf')) # get results of imputation from R
	if method=='seasplit_mean':
		result=pandas2ri.ri2py(impts.na_seasplit(ro.FloatVector(data.values),algorithm='mean',option='mean')) # get results of imputation from R
	if method=='seasplit_median':
		result=pandas2ri.ri2py(impts.na_seasplit(ro.FloatVector(data.values),algorithm='mean',option='median')) # get results of imputation from R
	if method=='seasplit_mode':
		result=pandas2ri.ri2py(impts.na_seasplit(ro.FloatVector(data.values),algorithm='mean',option='mode')) # get results of imputation from R
	if method=='seasplit_random':
		result=pandas2ri.ri2py(impts.na_seasplit(ro.FloatVector(data.values),algorithm='random')) # get results of imputation from R
	if method=='seasplit_kalman':
		result=pandas2ri.ri2py(impts.na_seasplit(ro.FloatVector(data.values),algorithm='kalman')) # get results of imputation from R
	if method=='seasplit_ma':
		result=pandas2ri.ri2py(impts.na_seasplit(ro.FloatVector(data.values),algorithm='ma')) # get results of imputation from R
	
	
	
	data=pd.Series(index=data.index,data=np.reshape(result,newshape=data.shape, order='C')) # construct DataFrame using original index and columns
	return data


a = ('2',)
b = 'z'
(b,)+a


impts=importr('imputeTS') # package for time series imputation
params={'random':{'method':impts.na_random},
		'mean':{'method':impts.na_mean},
		'ma':{'method':impts.na_ma},
		'locf':{'method':impts.na_locf},
		'interpol':{'method':impts.na_interpolation},
		'seadec':{'method':impts.na_seadec},
		'seasplit':{'method':impts.na_seasplit},
		'kalman':{'method':impts.na_kalman}
	}	

	if isinstance(obj,dict):
		result+=[[(key,)+a for a in o2t(args)] for key,args in obj.items()]
	for el in obj:
		if not isinstance(el, dict): result+=[(el,)]
		else: result+=[[(key,)+a for a in o2t(args)] for key,args in obj.items()]
	return result
	
	if not isinstance(obj,dict): return [(obj,)]
	else: return [[[(kw,)+a for a in o2t(arg)] for arg in args] for kw,args in obj.items()]

methods=[{'name':'random','alg':impts.na_random,'opt':random},
		{'name':'mean','alg':impts.na_mean,'opt':mean},
		{'name':'ma','alg':impts.na_ma,'opt':ma},
		{'name':'locf','alg':impts.na_locf,'opt':locf},
		{'name':'interpol','alg':impts.na_interpolation,'opt':interpol},
		{'name':'kalman','alg':impts.na_kalman,'opt':kalman},
		
		{'name':'seadec','alg':impts.na_seadec,'opt':{'algorithm':{'random':random,'mean':mean,'ma':ma,'locf':locf,'interpolation':interpol,'kalman':kalman}}},
		{'name':'seasplit','alg':impts.na_seasplit,'opt':{'algorithm':{'random':random,'mean':mean,'ma':ma,'locf':locf,'interpolation':interpol,'kalman':kalman}}}]	



# converts options to tuples
def o2t(d):
	result=[] # 
	for key,args in d.items():
		if not isinstance(args,dict): result+=[[(key,arg) for arg in args]]
		else:
			for k,a in args.items(): result+=[[[(key,k)]]+o2t(a)]
	return result
	
# converts options to kwargs
def o2k(methods):
	result=[]
	for l in o2t(methods): # for each list of tuples
		comb=product(*l) # all combinations of tuples
		for c in comb: result+=[{kw:arg for kw,arg in c}] # convert combination to dictionary
	return result


data=pd.read_csv(path,header=0,sep=";",usecols=[0,1,2], names=['date','time','load'],dtype={'load': np.float64},na_values=['?'], parse_dates=['date'], date_parser=(lambda x:pd.to_datetime(x,format='%d/%m/%Y'))) # read csv
data['hour']=pd.DatetimeIndex(data['time']).hour # new column for hours
data['minute']=pd.DatetimeIndex(data['time']).minute # new column for minutes
data.set_index(keys=['hour','minute'], append=True, inplace=True) # append hour and minute as new multiindex levels
data=(data*1000)/60 # convert kW to Wh
data.drop('time',axis=1,inplace=True) # drop time column
data=pd.pivot_table(data,index=['hour','minute'], columns='minute', values='load') # pivot so that minutes are columns, date & hour multi-index and load is value
data=order(data) # order data if necessary


f,_,_=data.index.min() # first day
	l,_,_=data.index.max() # last day
	if len(data.loc[f])<24*60: # if first day is incomplete
		data=data.drop(f,level=0) # drop the whole day
	if len(data.loc[l])<24*60: # if last day is incomplete
		data=data.drop(l,level=0) # drop the whole day
	



for name,data in weather_split.items():
	train_w,test_w=dp.train_test(data=data, test_size=0.255, base=7) # split into train & test sets
	dp.save(data=train_w,path=wip_dir+'train_'+name+'.csv') # save train set
	dp.save(data=test_w,path=wip_dir+'test_'+name+'.csv') # save test set
	dp.save_dict(dic=dp.split(train_w,nsplits=7), path=wip_dir+'train_'+name+'_') # split train set according to weekdays and save each into a separate file
	dp.save_dict(dic=dp.split(test_w,nsplits=7), path=wip_dir+'test_'+name+'_') # split test set according to weekdays and save each into a separate file


import figures as f

# Simple plot
fig, ax  = f.newfig(0.6)

def ema(y, a):
    s = []
    s.append(y[0])
    for t in range(1, len(y)):
        s.append(a * y[t] + (1-a) * s[t-1])
    return np.array(s)
    
y = [0]*200
y.extend([20]*(1000-len(y)))
s = ema(y, 0.01)

ax.plot(s)
ax.set_xlabel('X Label')
ax.set_ylabel('EMA')

img_dir='C:/Users/SABA/Google Drive/mtsg/text/img/'

f.p2l(img_dir + 'test')
	
	mu, sigma = 100, 15
x = mu + sigma*np.random.randn(10000)

# the histogram of the data
n, bins, patches = plt.hist(x, 50, normed=1, facecolor='green', alpha=0.75)


plt.xlabel('Smarts')
plt.ylabel('Probability')
plt.title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
plt.axis([40, 160, 0, 0.03])
plt.grid(True)

plt.show()

# plot heatmap of missing values
data_dir='C:/Users/SABA/Google Drive/mtsg/data/' # directory containing data 
data=dp.load(path=data_dir+'data.csv', idx='datetime',cols='load',dates=True) # load data
data=dp.cut(data=data,freq=1440) # remove incomplete first and last days
data=pd.DataFrame(data)
data=data.isnull()
data['time']=data.index.time
data['date']=data.index.date
data=pd.pivot_table(data, values='load' , index='date', columns='time',dropna=False)
cols = ('dodgerblue','aliceblue')
cmap = LinearSegmentedColormap.from_list('Custom', cols, len(cols))

sns.set(font_scale=1.75)
f,ax=plt.subplots() # get axis handle
ax=sns.heatmap(data,cmap=cmap) # produce heatmap
ax.set_xticks([i*240 for i in range(7)])
ax.set_xticklabels(['00:00','04:00','08:00','12:00','16:00','20:00','24:00'],fontsize=16)
ax.set_yticks([i*240 for i in range(7)])
ax.set_yticklabels([1440,1200,960,720,480,240,0],fontsize=16)
plt.yticks(rotation=0)
ax.set_xlabel('Time',fontsize=18)
ax.set_ylabel('Day',fontsize=18)
col_bar = ax.collections[0].colorbar
col_bar.set_ticks([0.25, 0.75])
col_bar.set_ticklabels(['data','outage'])



ax.set_frame_on(True)
col_bar.set_edgecolor('k')




import seaborn as sns
sns.set_style("ticks")



# plot bars  for missing values
def nan_bar(data):
	nans=data.isnull().sum(axis=1) # count NaNs row-wise
	nans.plot(kind='bar') # plot histogram of missing values,
	return

# REFORMAING IMPUTATION TABLE

results=pd.DataFrame()
for index, row in dp.load(path=data_dir + 'experiments/imp/imp.csv', idx='method').iterrows():
	col_vals={}
	for par in re.split(r',',index): 
		if ':' in par: col_vals[par.split(':')[0]]=par.split(':')[1]
		else: col_vals[par]=True
	for col,value in row.iteritems(): col_vals[col]=value
	result=pd.DataFrame(data=col_vals,index=[index]) 
	results=pd.concat([results,result], axis=0, join='outer')
results.index.name='method'
results=results.fillna(value=False)
results['SRMSE']=results['SRMSE']*100
results['MASE']=results['MASE']*10000
results['SMAPE']=results['SMAPE']*10000

ma=results.loc[results['alg'] == 'ma']
ma=ma.sort_values(by=['SRMSE','MASE','SMAPE','SMAE'])
ma=ma[['prep','weighting','window','SRMSE','MASE','SMAPE','SMAE']]
dp.save(data=ma, path=data_dir + 'experiments/imp/ma.csv', idx='method')

interpol=results.loc[results['alg'] == 'interpol']
interpol=interpol.sort_values(by=['SRMSE','MASE','SMAPE','SMAE'])
interpol=interpol[['prep','option','SRMSE','MASE','SMAPE','SMAE']]
dp.save(data=interpol, path=data_dir + 'experiments/imp/interpol.csv', idx='method')

other=results.loc[~results['alg'].isin(['interpol','ma'])]
other=other.sort_values(by=['SRMSE','MASE','SMAPE','SMAE'])
other=other[['prep','alg','SRMSE','MASE','SMAPE','SMAE']]
dp.save(data=other, path=data_dir + 'experiments/imp/other.csv', idx='method')	


X=data.select(lambda x:x[0] not in [Y_lab], axis=1) # everything not labelled "target" is a pattern, [0] refers to the level of multi-index
	X=data[data.columns.drop(labels=[Y_lab],level=0)]
	data.loc[idx[:,~data.columns.get_level_values(0).isin([ts])], :]
	
def X_Y(data,Y_lab='targets'):
	Y=data[Y_lab] # targets
	X=data.drop(Y_lab,axis=1,level=0)
	X=X.reindex_axis(sorted(X.columns), axis=1)
	Y=Y.reindex_axis(sorted(Y.columns), axis=1)
	return X, Y





loss.plot()

	
	T_X,T_Y=dp.X_Y(data=T,Y_lab='targets') # create patterns & targets in the correct format
	V_X,V_Y=dp.X_Y(data=V,Y_lab='targets') # patterns for forecasting



perf,loss=ev(train,test,model=model,prep=dp.de_mean,postp=dp.re_mean) # evaluate network




batch=28 # batch size for cross validation

model=nn(n_in=48, n_out=48, n_hid=100,dropout=0.1,hid_act='sigmoid',out_act='softmax',opt='rmsprop') # compile neural network
pred=pd.DataFrame() # dataframe for predictions
loss=pd.DataFrame() # dataframe for loss function
for i in range(0,len(test),batch): # for each batch
	if (len(test)-i)<batch: val_size=len(test)-i # not enough observation for complete batch
	else: val_size=batch # smaller batch 
	T=pd.concat([train,test[:i+val_size]]) # add new batch to train test
	mean,std=dp.mean_std(T[:len(T)-val_size]) # get mean and std only from train set
	T=dp.z_val(data=T,mean=mean,std=std) # standardize data
	T=dp.add_lags(data=T, lags=[7], nolag='targets') # add lags
	V=T[len(T)-val_size:] # build validation set
	T=T[:len(T)-val_size] # build train set
	T_X,T_Y=dp.X_Y(data=T,Y_lab='targets') # create patterns & targets in the correct format
	V_X,V_Y=dp.X_Y(data=V,Y_lab='targets') # patterns for forecasting
	#model.fit(T_X.as_matrix(), T_Y.as_matrix(), nb_epoch=100, batch_size=28,verbose=2,validation_data=(V_X.as_matrix(),V_Y.as_matrix()),callbacks=[stop]) # train neural network
	hist=model.fit(T_X.as_matrix(), T_Y.as_matrix(), nb_epoch=100, batch_size=100,verbose=2,validation_data=(V_X.as_matrix(),V_Y.as_matrix())) # train neural network
	V_pred=pd.DataFrame(model.predict(V_X.as_matrix()),index=V_Y.index,columns=V_Y.columns) # forecasts for the next batch
	V_pred=dp.z_inv(data=V_pred, mean=mean, std=std) # de-standardize data 
	pred=pd.concat([pred,V_pred]) # add new predictions
	new_loss=pd.DataFrame(hist.history) # new loss
	loss=pd.concat([loss,new_loss],axis=0,ignore_index=True) # append to old loss
pf.ev(pred=pred, true=true, label='nn', measures=measures) # evaluate performance
loss.plot()






dp.save(data=pred, path=exp_dir+'nn.csv', idx='date')







data=dp.add_lags(data=data, lags=[1], nolag='targets') # add lagged observations



# set grid search parameters and ranges
grid_space={'n_hidden':[10,20,30],
			'nb_epoch':[500,1000,1500,2000],
			'batch_size':[1,5,10,20]
		}

for i in range(1,6): # optimize for number of time steps
	X,Y=dp.split_X_Y(dp.shift(load_with_nans,n_shifts=i,shift=1).dropna()) # create patterns & targets in the correct format
	X=dp.order(X) # put timesteps in the correct order starting from the oldest
	grid_space['n_in']=[X.shape[1]] # workaround for enabling varying pattern lengths corresponding to the number of time steps
	model=KerasRegressor(build_fn=create_model,verbose=0) # create model template
	grid_setup = GridSearchCV(estimator=model, param_grid=grid_space, cv=TimeSeriesSplit(n_splits=3),n_jobs=1, scoring=make_scorer(r2_score,multioutput='uniform_average'), verbose=10) # set up the grid search
	grid_result = grid_setup.fit(X.as_matrix(), Y.as_matrix()) # fit best parameters
	# summarize results
	print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_)) # print best parameters
	means = grid_result.cv_results_['mean_test_score']
	stds = grid_result.cv_results_['std_test_score']
	params = grid_result.cv_results_['params']
	for mean, stdev, param in zip(means, stds, params):	print("%f (%f) with: %r" % (mean, stdev, param)) # print all sets of parameters

plt.plot(grid_result.best_estimator_.predict(X.as_matrix())[0])

f,ax=plt.subplot()


exp_dir='C:/Users/SABA/Google Drive/mtsg/data/experiments/es_week/' # directory containing results of experiments

dp.merge_dir_files(exp_dir)

# aggregate errors
exp_dir='C:/Users/SABA/Google Drive/mtsg/data/experiments/' # directory containing results of experiments
ets=dp.load(exp_dir+'ets/ha,ets.csv',idx='date',dates=True) # load best predictions
arma=dp.load(exp_dir+'arima/ha,dec,arima.csv',idx='date',dates=True) # load best predictions
armax=dp.load(exp_dir+'arimax/ha,fregs,arimax.csv',idx='date',dates=True) # load best predictions
res=pd.DataFrame()
res['ets']=dp.d2s(pred-true) # ets residuals
res['arma']=dp.d2s(arma-true) # ets residuals
res['armax']=dp.d2s(armax-true) # ets residuals
res=pd.DataFrame({col: res[col].sort_values(ascending=False).values for col in res.columns.values})
res.plot(logy=True)


# computes min & mean rank according to performance measures
def rank(data):
	sum_perf=data.sum(axis='columns') # sum performance measures
	data['mean_rank']=data.rank(method='dense',ascending=True).mean(axis='columns') # add column with mean rank
	data['min_rank']=data.rank(method='dense',ascending=True).min(axis='columns') # add column with mean rank
	data['sum']=sum_perf # add sum column
	data=data.sort_values(by=['sum','mean_rank','min_rank']) # sort by rank
	#data=data.drop(['sum'],axis='columns') # remove unnecessary columns
	return data
