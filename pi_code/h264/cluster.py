from sklearn.datasets import make_blobs
from sklearn.cluster import DBSCAN
import time
import numpy as np
import math
import traceback
from os import listdir, makedirs
import sys

import shutil
import pickle
from mylog import MyLog

import cv2
from decider import Decider
from config import Configuration

def correlationInCluster(X, epsilon, min_samples, imWidth, imHeight):
	"calculates only the correlation"
	if len(X) == 0:
		return (None, None, None)
	# Compute DBSCAN
	db = DBSCAN(eps=epsilon, min_samples=min_samples).fit(X)
	labels = db.labels_
	correlation={}
	xvalues={}
	yvalues={}

	for clusterno in np.unique(labels):
		correlation[int(clusterno)]=0.0
		xvalues[int(clusterno)]=[]
		yvalues[int(clusterno)]=[]

		#korelation for every cluster
	#group the x and y values of every cluster
	for pos in range(0,len(labels)):
		#get its clusterno
		clusterno = labels[pos]
		point =X[pos]
		xvalues[clusterno].append(point[0])
		yvalues[clusterno].append(point[1])
		
	for cluster in xvalues.keys():
		if len(xvalues[cluster]) > 1:
			correvals = np.corrcoef(xvalues[cluster], yvalues[cluster])
			correlation[cluster]=(math.fabs(correvals[0,1]))
	return correlation, xvalues, yvalues


def calculateCluster(X, epsilon, min_samples, imWidth, imHeight):
	if len(X) == 0:
		return (None, None, None, None, None, None, None)
	# Compute DBSCAN
	db = DBSCAN(eps=epsilon, min_samples=min_samples).fit(X)
	labels = db.labels_

	cldictx ={}
	cldicty={}
	correlation={}
	xvalues={}
	yvalues={}
	weights={}
	xNormvalues={}
	yNormvalues={}
	pointsInCluster={}
	cov00={}
	cov01={}
	cov11={}

	#initialise dictionaries with no of clusters
	for clusterno in np.unique(labels):
		cldictx[int(clusterno)]=0.0
		cldicty[int(clusterno)]=0.0
		correlation[int(clusterno)]=0.0
		xvalues[int(clusterno)]=[]
		yvalues[int(clusterno)]=[]
		xNormvalues[clusterno]=[]
		yNormvalues[clusterno]=[]
		weights[int(clusterno)]=0.0
		pointsInCluster[int(clusterno)]=0

	#for every point
	for pos in range(0, len(labels)):
		#get its clusterno
		clusterno=labels[pos]
		#count the number of entries in cluster
		pointsInCluster[clusterno]=pointsInCluster[clusterno]+1
		#get the current point at the position
		point =X[pos]
		#make the points relative to 100% imWidth and Height
		point[0]=point[0]/imWidth
		point[1]=point[1]/imHeight
		x=cldictx[clusterno]
		y=cldicty[clusterno]
		cldictx[clusterno]=x+point[0]
		cldicty[clusterno]=y+point[1]


	for clusterno in np.unique(labels):
		cldictx[clusterno]=round(cldictx[clusterno]/pointsInCluster[clusterno], 6)
		cldicty[clusterno]=round(cldicty[clusterno]/pointsInCluster[clusterno],6)
		weights[clusterno]=round(pointsInCluster[clusterno]/len(X),6)
		
	#korelation for every cluster
	#group the x and y values of every cluster
	for pos in range(0,len(labels)):
		#get its clusterno
		clusterno = labels[pos]
		point =X[pos]
		xvalues[clusterno].append(point[0])
		yvalues[clusterno].append(point[1])
		xNormvalues[clusterno].append(point[0]-cldictx[clusterno])
		yNormvalues[clusterno].append(point[1]-cldicty[clusterno])

	for cluster in xvalues.keys():
		if len(xvalues[cluster]) > 1:
			covariance= np.cov(xNormvalues[cluster], yNormvalues[cluster])
			cov00[cluster]=covariance[0,0]
			cov01[cluster]=covariance[0,1]
			cov11[cluster]=covariance[1,1]
			correvals = np.corrcoef(xvalues[cluster], yvalues[cluster])
			correlation[cluster]=(math.fabs(correvals[0,1]))

	return (cldictx, cldicty, correlation, cov00, cov01, cov11, weights)

def calculateClusterWithDimension(X, epsilon, min_samples):
	if len(X) == 0:
		return (None, None, None, None, None, None, None)
	# Compute DBSCAN
	db = DBSCAN(eps=epsilon, min_samples=min_samples).fit(X)
	labels = db.labels_

	cldictx ={}
	cldicty={}
	correlation={}
	xvalues={}
	yvalues={}
	dimension={}
	xNormvalues={}
	yNormvalues={}
	pointsInCluster={}
	cov00={}
	cov01={}
	cov11={}

	#initialise dictionaries with no of clusters
	for clusterno in np.unique(labels):
		cldictx[int(clusterno)]=0.0
		cldicty[int(clusterno)]=0.0
		correlation[int(clusterno)]=0.0
		xvalues[int(clusterno)]=[]
		yvalues[int(clusterno)]=[]
		xNormvalues[clusterno]=[]
		yNormvalues[clusterno]=[]
		dimension[int(clusterno)]=0.0
		pointsInCluster[int(clusterno)]=0

	#for every point
	for pos in range(0, len(labels)):
		#get its clusterno
		clusterno=labels[pos]
		#count the number of entries in cluster
		pointsInCluster[clusterno]=pointsInCluster[clusterno]+1
		#get the current point at the position
		point =X[pos]
		#make the points relative to 100% imWidth and Height
		point[0]=point[0]
		point[1]=point[1]
		x=cldictx[clusterno]
		y=cldicty[clusterno]
		cldictx[clusterno]=x+point[0]
		cldicty[clusterno]=y+point[1]



	for clusterno in np.unique(labels):
		cldictx[clusterno]=round(cldictx[clusterno]/pointsInCluster[clusterno], 6)
		cldicty[clusterno]=round(cldicty[clusterno]/pointsInCluster[clusterno],6)
		
	#korelation for every cluster
	#group the x and y values of every cluster
	for pos in range(0,len(labels)):
		#get its clusterno
		clusterno = labels[pos]
		point =X[pos]
		xvalues[clusterno].append(point[0])
		yvalues[clusterno].append(point[1])
		xNormvalues[clusterno].append(point[0]-cldictx[clusterno])
		yNormvalues[clusterno].append(point[1]-cldicty[clusterno])

	for cluster in xvalues.keys():
		if len(xvalues[cluster]) > 1:
			covariance= np.cov(xNormvalues[cluster], yNormvalues[cluster])
			cov00[cluster]=covariance[0,0]
			cov01[cluster]=covariance[0,1]
			cov11[cluster]=covariance[1,1]
			#calculate the size of the ellipse for filtering
			eigenVal_percent, eigenVec_percent=cv2.eigen(covariance, eigenvalues=True)[1:]
			lenVecEins = [eigenVec_percent[0][0]*eigenVal_percent[0], eigenVec_percent[0][1]*eigenVal_percent[0]]
			lenVecZwei = [eigenVec_percent[1][0]*eigenVal_percent[1], eigenVec_percent[1][1]*eigenVal_percent[1]]

			betragEins=math.sqrt(sum(i*i for i in lenVecEins))
			betragZwei=math.sqrt(sum(i*i for i in lenVecZwei))
			dimension[cluster] =math.sqrt(9.210*abs(betragEins))* math.sqrt(9.210*abs(betragZwei))

			correvals = np.corrcoef(xvalues[cluster], yvalues[cluster])
			correlation[cluster]=(math.fabs(correvals[0,1]))

	return (cldictx, cldicty, correlation, cov00, cov01, cov11, dimension)
