import pandas as pd
import numpy as np
import random

import scipy as scp
import sklearn

from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn import metrics 
from sklearn.metrics import confusion_matrix
from sklearn.linear_model import LinearRegression

import statsmodels.api as sm
import matplotlib.pyplot as plt

from causallearn.search.ConstraintBased.PC import pc
from causallearn.utils.cit import fisherz, chisq
from causallearn.utils.GraphUtils import GraphUtils


import os
# Get the directory path of the current Python script (algorithm1.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Encode text values to indexes(i.e. [1],[2],[3]).
def encode_text_index(df):
    le = preprocessing.LabelEncoder()
    for col in df.columns:
        df[col] = le.fit_transform(df[col])
    return le.classes_

# To classify a column is categorical or continious
def is_categorical(array_like):
    return array_like.dtype.name == 'object'

def debias_hiring_dataset():
    # Construct the file path using BASE_DIR
    file_path = os.path.join(current_dir, 'debiased_Hiring (Synthetic).csv')

    data = pd.read_csv(file_path, na_values=['NA','?']) 

    columnNames = data.columns
    columnNames = columnNames.tolist()
    
    # Create a list named columnType to hold its categorical or not
    columnType = data.apply(is_categorical).tolist()

    # Data Encoding
    data_ip = data.copy(deep=True)
    encode_text_index(data_ip)

    for i in range(4000):
        if(data_ip['Major'][i] == 0):
            data_ip['Major'][i] = 1
        else:
            data_ip['Major'][i] = 0
            
    for i in range(4000):
        if(data_ip['College_Rank'][i] == 0):
            data_ip['College_Rank'][i] = 1
        else:
            data_ip['College_Rank'][i] = 0
            
    for i in range(4000):
        if(data_ip['Job'][i] == 0):
            data_ip['Job'][i] = 1
        else:
            data_ip['Job'][i] = 0
            
    for i in range(4000):
        if(data_ip['Grade_Point_Average'][i] == 0):
            data_ip['Grade_Point_Average'][i] = 1
        else:
            data_ip['Grade_Point_Average'][i] = 0

    for i in range(4000):
        if(data_ip['Race'][i] == 0):
            data_ip['Race'][i] = 1
        else:
            data_ip['Race'][i] = 0
     
    print(data_ip)       
    return data_ip, columnNames, columnType


def edgeMatrixToFrontend(edgeMatrix):
    transpose_edgeMatrix = [list(row) for row in zip(*edgeMatrix)]

    for i in range(len(transpose_edgeMatrix)):
        for j in range(len(transpose_edgeMatrix[i])):
            
            if transpose_edgeMatrix[i][j] == -1 and transpose_edgeMatrix[j][i] == -1:
                transpose_edgeMatrix[j][i] = 0
            elif transpose_edgeMatrix[i][j] == -1:
                transpose_edgeMatrix[i][j] = 0
                
    return transpose_edgeMatrix

def dataToDAG_PC(p_value, data_ip):
    
    pValue = float(p_value)
           
    dag_data_ip = data_ip.to_numpy()

    #pc algorithm
    cg = pc(dag_data_ip, pValue, fisherz, True, 0,-1)  # Run PC and obtain the estimated graph (CausalGraph object)
    #print(cg.G.graph.tolist())
    
    # Edge Matrix
    edgeMatrix = cg.G.graph.tolist()
    
    print("Edge Matrix = ", edgeMatrix)
    
    return edgeMatrix
