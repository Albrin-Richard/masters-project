import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression

def train_xy_numerical(X, y, coefficientMatrix, interceptMatrix, edgeWeight, columnNames):
    model = LinearRegression(fit_intercept=True)
    model.fit(X,y)
    
    
    toMajor_intercept = model.intercept_
    
    
    toMajor_edge_weights = (model.coef_)[0]
    print("Edge weight = ",toMajor_edge_weights)
    print("----------------------")
    
    x_index = [columnNames.index(X.columns[i]) for i in range(len(X.columns))]

    y_index = columnNames.index(y.columns[0])
    
    interceptMatrix[y_index] = toMajor_intercept[0]
    for i in range(len(X.columns)):

        coefficientMatrix[y_index][x_index[i]] = toMajor_edge_weights[i]
        edgeWeight[y_index][x_index[i]] = round( toMajor_edge_weights[i] , 2)
    
    return coefficientMatrix, interceptMatrix, edgeWeight

def train_xy_categorical(X, y, coefficientMatrix, interceptMatrix, edgeWeight, columnNames):
    
    model = LogisticRegression(random_state=0, multi_class='multinomial', penalty=None, solver='newton-cg').fit(X, y)

    preds = model.predict(X)

    #print the tunable parameters (They were not tuned in this example, everything kept as default)
    #params = model.get_params()
    #print(params)

    #score = model.score(X, y)
    #print("----------------------")
    #print('-->Test Accuracy Score', score)
    
    #toMajor_intercept = np.exp(model.intercept_)
    #print("Intercept = ",toMajor_intercept)

    toMajor_edge_weights = np.exp(model.coef_)
    #print("Before Edge weight = ",model.coef_)
    print("Edge weight = ",toMajor_edge_weights)
    print("----------------------")

    x_index = [columnNames.index(X.columns[i]) for i in range(len(X.columns))]
    #print(x_index)
    y_index = columnNames.index(y.columns[0])
    #print(y_index)
    
    interceptMatrix[y_index] = (model.intercept_)
    for i in range(len(X.columns)):
        #print(X.columns[i]," -->", y.columns[0]," = " ,toMajor_edge_weights[i])
        coefficientMatrix[y_index][x_index[i]] = [coefs[i] for coefs in model.coef_]
        
        # Calculate the average of all elements in the list
        edge_weight_list = [edge_weights[i] for edge_weights in toMajor_edge_weights]
        edgeWeight[y_index][x_index[i]] = round(sum(edge_weight_list) / len(edge_weight_list) , 2)
        
    return coefficientMatrix, interceptMatrix, edgeWeight

# Relational Dictionary to keep track of Child and Parent nodes
def findRelation(edgeMatrix, columnNames):
    relationDict = {}
    for row in range(len(columnNames)):
        parent = []
        for column in range(len(columnNames)):
            if(edgeMatrix[row][column] == 1):
                #print(columnNames[column], "-->", columnNames[row])
                parent.append(columnNames[column])      

        if(parent != []):
            relationDict[columnNames[row]] = parent

    print(relationDict)
    return relationDict


def getEdgeWeight(data_ip, columnType, edgeMatrix):
    
    
    columnNames = data_ip.columns.tolist()
    
    matrixSize = len(columnNames)  # size of matrix

    #-------- Coefficient matrix ------------------#
    coefficientMatrix = [[0 for j in range(matrixSize)] for i in range(matrixSize)]
    #print(coefficientMatrix)

    #-------- Intercept matrix ------------------#
    interceptMatrix = [0 for i in range(matrixSize)]
    #print(interceptMatrix)

    #-------- Edge Weight matrix ------------------#
    edgeWeight = [[0 for j in range(matrixSize)] for i in range(matrixSize)]


    relationDict = findRelation(edgeMatrix, columnNames)
    print("Edge Mat = ", edgeMatrix)
    print("Relation = ", relationDict)
    
    # Train and obtain coefficients of edges (edge weights) and Intercept
    for key in relationDict:
        #print(key, '<-', relationDict[key])
        X = data_ip[relationDict[key]]
        y = data_ip[[key]]
        
        if(columnType[data_ip.columns.get_loc(key)]  == True):
            print("Categorical")
            train_xy_categorical(X, y, coefficientMatrix, interceptMatrix, edgeWeight, columnNames)
        else:
            print("Numeric")
            train_xy_numerical(X, y, coefficientMatrix, interceptMatrix, edgeWeight, columnNames)
    
    
    print("Edge weight = ", edgeWeight)
            
    return coefficientMatrix, interceptMatrix, edgeWeight