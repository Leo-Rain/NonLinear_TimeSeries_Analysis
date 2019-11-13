# Functions for computations of
    # (1) A recurrence Plot
    # (2) Recurrence Entropy defined from the probability of
    #     occurence of microstates of size n by n in the
    #     recurrence plot

# functions to create recurrence plot
import numpy as np
#import matplotlib.pyplot as plt
from scipy import signal, spatial
from scipy.spatial.distance import pdist,cdist, squareform
from sklearn.feature_extraction import image
import itertools
import random

# Function to compute a recurrence plot
# Inputs :
    # time series: the time series you are looking at
    # eps: the epsilon treshold
# Outputs
    # A n by n matrix, with n being the length of time Series
def recurrencePlot(timeSeries, eps):
    # length of the time series
    dimT = len(timeSeries)
    # All distances between all points in the time series
    d = cdist(timeSeries[:,None],timeSeries[:,None],metric='euclidean')
    # flatten the matrix
    flattenedD = d.flatten()
    # Change to 1 (0) all entries <= (>) eps
    binaryD = np.transpose([1 if x<=eps else 0 for x in flattenedD])
    # Format the result in a len by len matrix (the recurrence matrix)
    recurrenceMatrix = binaryD.reshape((dimT, dimT))
    return recurrenceMatrix

# Function to compute the recurrence entropy


def recurrenceEntropy(timeSeries, eps,n,sampleSize):
    # Construct the recurrence plot
    rPlot = recurrencePlot(timeSeries, eps)
    # dimension of a microstate: n^2
    # Consider all Patches of dimension n^2
    allPatches = image.extract_patches_2d(rPlot, (n, n))
    # I want to consider just a random sample of all these patches.
    # Sample size
    sampledMicrostates = random.sample(list(allPatches),sampleSize)
    # I count the occurence of microstates in the recurrence Matrix
    occurenceList = np.unique(sampledMicrostates,axis=0, return_counts=1)[1]
    # From a list of occurences I compute the probability of
    probabilityList = occurenceList/float(sampleSize)
    # given the probability list we can define a recurrence entropy based on microstates in RP
    # Step (1) remove all zeros
    noZerosProbabilityList =  probabilityList[probabilityList>0]
    # Step (2) compute the Shannon Entropy of the Probability of occurence of those microstates
    entropy = - np.sum(noZerosProbabilityList * np.log(noZerosProbabilityList))
    # Max Entropy (found analytically)
    maxEntropy = np.log(sampleSize)
    # Normalized entropy
    normalizedEntropy = entropy/maxEntropy

    return normalizedEntropy



# Function to compute the recurrence entropy in a faster way
# Instead of computing the RP, I compute directly the microstates.
def recurrenceEntropyFAST(timeSeries, eps,n,sampleSize):
    # dimension of a microstate: n^2
    # Consider all Patches of dimension n^2
    # length of the time series
    dimT = len(timeSeries)
    # Initialize microstates
    micro = np.array([], float)

    for i in range(sampleSize):
        # Bounds
        a = random.randint(0, dimT-n)
        b = random.randint(0, dimT-n)
        # Consider 4 consecutive times  t(n),t(n+1),t(n+2),t(n+3)
        # Choose the randomly. Then do the same t(n),t(n+1),t(n+2),t(n+3)
        # All distances between all points in the time series
        d = cdist(timeSeries[a:a+n,None],timeSeries[b:b+n,None],metric='euclidean')
        # Heaviside function
        d[d<=eps]=1
        d[(d>eps)&(d!=1)]=0
        micro = np.append(micro, d)
        # reshape the microstates
    microstates = micro.reshape((sampleSize,n,n))
    occurenceList = np.unique(microstates,axis=0, return_counts=1)[1]
    # From a list of occurences I compute the probability of
    probabilityList = occurenceList/float(sampleSize)
    # given the probability list we can define a recurrence entropy based on microstates in RP
    # Step (1) remove all zeros
    noZerosProbabilityList =  probabilityList[probabilityList>0]
    # Step (2) compute the Shannon Entropy of the Probability of occurence of those microstates
    entropy = - np.sum(noZerosProbabilityList * np.log(noZerosProbabilityList))
    # Max Entropy (found analytically)
    maxEntropy = np.log(sampleSize)
    # Normalized entropy
    normalizedEntropy = entropy/maxEntropy

    return normalizedEntropy

# Function to compute the recurrence entropy over an entire field
# This one is coded in order to test differences in results giving a different epsilon
# Epsilon is already computed
def recurrenceEntropyField(field,epsilonField,n,sampleSize):

    # Dimensions of the field?
    # Time dimension
    dimTime = np.shape(field)[0]
    # Number of points in latitude (y-axis)
    dimLat = np.shape(field)[1]
    # Number of points in longitude (x-axis)
    dimLon = np.shape(field)[2]

    # Initialize the entropy field
    entropyField = np.zeros([dimLat,dimLon])
    normalizedEntropyField = np.zeros([dimLat,dimLon])

    for i in range(0,dimLat):
        for j in range(0,dimLon):
            # Check if is a masked value
            if np.isnan(field[0,i,j]):
                entropyField[i,j] = field[0,i,j] # if it is mask just return the mask
            else:
                entropyField[i,j] = recurrenceEntropy(field[:,i,j],epsilonField[i,j],n,sampleSize)[0]

    return entropyField


'''
# Function to compute the recurrence entropy over an entire field
# This one is coded in order to test differences in results giving a different epsilon
# It compute epsilon as a percentage of the standard deviation of the time series
# and it takes as input the percentage
def recurrenceEntropyField(field,n,sampleSize):

    # Dimensions of the field?
    # Time dimension
    dimTime = np.shape(field)[0]
    # Number of points in latitude (y-axis)
    dimLat = np.shape(field)[1]
    # Number of points in longitude (x-axis)
    dimLon = np.shape(field)[2]

    # Initialize the entropy field
    entropyField = np.zeros([dimLat,dimLon])
    normalizedEntropyField = np.zeros([dimLat,dimLon])

    for i in range(0,dimLat):
        for j in range(0,dimLon):
            # Check if is a masked value
            if np.isnan(field[0,i,j]):
                entropyField[i,j] = field[0,i,j] # if it is mask just return the mask
            else:
                # Compute epsilon as x percentage of standard dev of the time series
                diameter = np.abs(np.max(field[:,i,j]) - np.min(field[:,i,j]))
                eps = 0.05 * diameter
                entropyField[i,j] = recurrenceEntropy(field[:,i,j],eps,n,sampleSize)[0]

    return entropyField
 '''

'''
# Here if interested in performing some tests

# Function to compute the recurrence entropy over an entire field
# This one is coded in order to test differences in results giving a different epsilon
# It compute epsilon as a percentage of the standard deviation of the time series
# and it takes as input the percentage
def recurrenceEntropyFieldTestingEpsilon(field,percentage,n,sampleSize):

    # Dimensions of the field?
    # Time dimension
    dimTime = np.shape(field)[0]
    # Number of points in latitude (y-axis)
    dimLat = np.shape(field)[1]
    # Number of points in longitude (x-axis)
    dimLon = np.shape(field)[2]

    # Initialize the entropy field
    entropyField = np.zeros([dimLat,dimLon])
    normalizedEntropyField = np.zeros([dimLat,dimLon])

    for i in range(0,dimLat):
        for j in range(0,dimLon):
            # Check if is a masked value
            if np.isnan(field[0,i,j]):
                entropyField[i,j] = field[0,i,j] # if it is mask just return the mask
            else:
                # Compute epsilon as x percentage of standard dev of the time series
                std =np.std(field[:,i,j], ddof = 1)
                eps = percentage * std
                entropyField[i,j] = recurrenceEntropy(field[:,i,j],eps,n,sampleSize)[0]
                normalizedEntropyField[i,j] = recurrenceEntropy(field[:,i,j],eps,n,sampleSize)[1]
    # This returns 2 numbers: [entropy, normalized entropy]
    return [entropyField,normalizedEntropyField]

# Function to compute the recurrence entropy over an entire field
# This one is coded in order to test differences in results giving a different epsilon
# It compute epsilon as a percentage of the max diameter of the time series
# and it takes as input the percentage
def recurrenceEntropyFieldPercentMaxDiameter(field,percentage,n,sampleSize):

    # Dimensions of the field?
    # Time dimension
    dimTime = np.shape(field)[0]
    # Number of points in latitude (y-axis)
    dimLat = np.shape(field)[1]
    # Number of points in longitude (x-axis)
    dimLon = np.shape(field)[2]

    # Initialize the entropy field
    entropyField = np.zeros([dimLat,dimLon])
    normalizedEntropyField = np.zeros([dimLat,dimLon])

    for i in range(0,dimLat):
        for j in range(0,dimLon):
            # Check if is a masked value
            if np.isnan(field[0,i,j]):
                entropyField[i,j] = field[0,i,j] # if it is mask just return the mask
            else:
                # Compute epsilon as x percentage of standard dev of the time series
                diameter = np.abs(np.max(field[:,i,j]) - np.min(field[:,i,j]))
                eps = percentage * diameter
                entropyField[i,j] = recurrenceEntropy(field[:,i,j],eps,n,sampleSize)[0]
                normalizedEntropyField[i,j] = recurrenceEntropy(field[:,i,j],eps,n,sampleSize)[1]
    # This returns 2 numbers: [entropy, normalized entropy]
    return [entropyField,normalizedEntropyField]
'''