import numpy as np
import pandas as pd

from collections import Counter

from algorithms.edge_weight import findRelation, train_xy_categorical, train_xy_numerical
from algorithms.pcDAG import edgeMatrixToFrontend

def dataset_debias(data_ip, columnType, edgeMatrix, coefficientMatrix, interceptMatrix, edgeWeightMatrix, Edges_added, Edges_modified):
    
    columnNames = data_ip.columns.tolist()
    
    #findRelation(edgeMatrix)
    print("edgeMatrix = ", edgeMatrix)
    print("coefficientMatrix = ", coefficientMatrix)
    print("interceptMatrix = ", interceptMatrix)
    print("edgeWeight = ", edgeWeightMatrix)
    #print("columnNames = ", columnNames)
    
    ## ---------- Newly Added Edges ------------- ##
    edges_added_copy = Edges_added[:]  # Create a copy to iterate over

    for new_edge in edges_added_copy:
        startNode = new_edge[0]
        endNode = new_edge[1]

        # Check if the edge is already present in the begining
        if edgeMatrix[endNode][startNode] == 1:
            Edges_added.remove(new_edge)
            #print("<--- edge is already present in the begining ")
        else:
            edgeMatrix[endNode][startNode] = 1  
        
    relationDict = findRelation(edgeMatrix, columnNames)
    
    ## ---------- Algo 6 - 9 ------------- ##
    # Retrain linear model for n as a function of its parents
    for addedEdge in Edges_added:
        
        # Node pointed by the newly added edge
        pointedNode = addedEdge[1]
        nodeName = columnNames[pointedNode]
        
        #retrain linear model for n as a function of its parents
        print(nodeName, '<-', relationDict[nodeName])
        X = data_ip[relationDict[nodeName]]
        y = data_ip[[nodeName]]
            
        if(columnType[data_ip.columns.get_loc(nodeName)]  == True):
            print("Categorical")
            coefficientMatrix, interceptMatrix, edgeWeightMatrix = train_xy_categorical(X, y, coefficientMatrix, interceptMatrix, edgeWeightMatrix, columnNames)
        else:
            print("Numeric")
            coefficientMatrix, interceptMatrix, edgeWeightMatrix = train_xy_numerical(X, y, coefficientMatrix, interceptMatrix, edgeWeightMatrix, columnNames)
    
   ## ------------------------------------- ##
   
    def dfs_descendants(node, edge_matrix, visited, descendants):
        visited[node] = True
        for i in range(len(edge_matrix[node])):
            if edge_matrix[i][node] == 1 and not visited[i]:
                descendants[i] = True
                dfs_descendants(i, edge_matrix, visited, descendants)

    def find_descendants(node, edge_matrix):
        visited = [False] * len(edge_matrix)
        descendants = [False] * len(edge_matrix)
        dfs_descendants(node, edge_matrix, visited, descendants)
        return [i for i in range(len(descendants)) if descendants[i]]
    
    def remove_duplicates_preserve_order(input_list):
        seen = set()
        result = []
        for item in input_list:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

   ## ---------- Algo 11 - 16 ------------- ##

    Vsim = []
    for edge in (Edges_added + Edges_modified):
        # Node pointed by the edge
        pointedNode = edge[1]
        nodeName = columnNames[pointedNode]
        
        #To find all descendants
        descendants = find_descendants(pointedNode, edgeMatrix)
        
        Vsim = Vsim + [nodeName] + [columnNames[i] for i in descendants]

    Vsim = remove_duplicates_preserve_order(Vsim) # Remove any duplicate entries in Vsim
    print("==> Vsim =", Vsim)
    ## ------------------------------------- ##
    
    def topological_sort(edge_matrix):
        num_nodes = len(edge_matrix)
        in_degree = [0] * num_nodes
        sorted_nodes = []

        # Calculate in-degree of each node
        for row in edge_matrix:
            for j in range(num_nodes):
                if row[j] == 1:
                    in_degree[j] += 1

        # Enqueue nodes with in-degree 0
        queue = []
        for i in range(num_nodes):
            if in_degree[i] == 0:
                queue.append(i)

        # Perform topological sort
        while queue:
            node = queue.pop(0)
            sorted_nodes.append(node)

            for j in range(num_nodes):
                if edge_matrix[node][j] == 1:
                    in_degree[j] -= 1
                    if in_degree[j] == 0:
                        queue.append(j)

        # Check if a cycle exists
        if len(sorted_nodes) != num_nodes:
            raise ValueError("The graph contains a cycle")

        print("-> Topological sorted = ", sorted_nodes)
        return sorted_nodes
    
    def softmax(x):
        """ Compute softmax values for each set of scores in x. """
        if x.shape[1] == 1:
            print("-----> 1D")
            e_x = 1/ (1+np.exp(-(x)))
            return e_x
        else:
            print("-----> 2D")
            # Multinomial classification (2D array)
            e_x = np.exp(x - np.max(x, axis=1)[:, np.newaxis])
            return e_x / e_x.sum(axis=1)[:, np.newaxis]

    def random_ri(input_list): 
        randomized_series = input_list.sample(frac=1, random_state=42)  # Randomize the series
        randomized_series = randomized_series.reset_index(drop=True)
        return randomized_series 
      
    ## ---------- Generate values based on Equation 2 ------------- ##
    
    # Create a blank Dict
    data_prob = {}
    
    def debias_SEM_categorical(dataset, coef, intercept, Vsim, strength):
    
        index = dataset.columns
        
        # Make a copy of the DataFrame
        dataset_randominess = dataset.copy()
        
        # ai edge strength
        ai = [1] * len(index)
        print(ai)
            
        for i, item in enumerate(Vsim):
            print(item)
            ai[dataset.columns.get_loc(item)] = strength[i]

            dataset_randominess[item] = random_ri(dataset[item])  
            
        print("after ai =", ai)
        output = 0
        output_randominess = 0
        
        for i in range(len(coef)):
            print("test ---->",  coef[i].reshape(1,-1).shape, "Value ---->",  coef[i].reshape(1,-1))
            output = output + np.dot(ai[i], np.dot(dataset[index[i]].values.reshape(-1,1), coef[i].reshape(1,-1)))
            output_randominess = output_randominess + np.dot((1 - ai[i]), np.dot(dataset_randominess[index[i]].values.reshape(-1,1), coef[i].reshape(1,-1)))
            

        output = output + intercept + output_randominess
        
        print("output = ", output, "dims = ",output.shape[1])
        # Calculate log probabilities for each data point
        #log_probabilities = output - np.log(np.sum(np.exp(output), axis=1)[:, np.newaxis])

        if output.shape[1] == 1:
            print("dims = ",output.shape[1])
            # Binary classification (1D array)
            log_probabilities = output
            class_probabilities = softmax(log_probabilities)
        
        else:
            # Multinomial classification (2D array)
            log_probabilities = output - np.log(np.sum(np.exp(output), axis=1)[:, np.newaxis])
            class_probabilities = softmax(log_probabilities)

        print("Log Probabilities (Log Odds): \n", log_probabilities)
        
        # Apply softmax to log probabilities to obtain class probabilities for each data point
        #class_probabilities = softmax(log_probabilities)
        
        print("Class Probabilities (Softmax): \n", class_probabilities)
        
        #output = sigmoid(output)
        
        #output = output.reshape(-1,1)
        # Get the index of the maximum probability for each data point
        #predicted_classes = np.argmax(class_probabilities, axis=1)  

        print("Shape = ",class_probabilities.shape)
        print("Prediction = ",class_probabilities)
        
        return class_probabilities

    def debias_SEM_continious(dataset, coef, intercept, Vsim, strength):
        
        index = dataset.columns
        
        # Make a copy of the DataFrame
        dataset_randominess = dataset.copy()
        
        # ai edge strength
        ai = [1] * len(index)
        print(ai)
            
        for i, item in enumerate(Vsim):
            print(item)
            ai[dataset.columns.get_loc(item)] = strength[i]

            dataset_randominess[item] = random_ri(dataset[item])  
            
        print("after ai =", ai)
        output = 0
        output_randominess = 0
    
        for i in range(len(coef)):
            output = output + np.dot(ai[i], np.dot(dataset[index[i]], coef[i]))
            output_randominess = output_randominess + np.dot((1 - ai[i]), np.dot(dataset_randominess[index[i]], coef[i]))
            
        output = output + intercept + output_randominess
        output = output.reshape(-1,1)
        
        return output
    
    def debias_categorical(X, y, Vsim, strength):

        if(len(X.columns) == 1 ):
            data_dbias[y] = random_ri(data_ip[y])
            data_prob[y] = data_dbias[y].values.reshape(-1, 1)


        else:
            endNodeNumber = columnNames.index(y)
            intercept = interceptMatrix[endNodeNumber]
            print("Intercept = ", intercept)
            coefficients = np.array([x for x in coefficientMatrix[endNodeNumber] if x != 0])
            print("Coefficient = ", coefficients)
            
            output = debias_SEM_categorical(X,coefficients,intercept,Vsim, strength)
            
            # Apply the function to each element in the 'int_column'
            #data_dbias[y] = data_dbias[y].apply(int_to_array)
            
            #print(" typeeees= ", type(data_dbias[y][0]))
            print("received output = ", output)
            
            #global data_prob  # Declare data_prob as a global variable
            
            # Create a DataFrame for 'output'
            data_prob[y] = output

            
            # Get the index of the maximum probability for each data point
            if output.shape[1] == 1:
                # Binary classification (1D array)
                #output = output.flatten()
                
                predicted_classes = np.where(output >= 0.5, 1, 0)
                predicted_classes = predicted_classes.reshape(-1,1)
            else:
                # Multinomial classification (2D array)
                
                predicted_classes = np.argmax(output, axis=1)
                predicted_classes = predicted_classes.reshape(-1,1)
            
            print(" typeeees= ", type(predicted_classes[0]))
            print("received =",predicted_classes)
            data_dbias[y] = predicted_classes

            print("received =",data_dbias[y])
            
    def debias_continuous(X, y, Vsim, strength): 
        endNodeNumber = columnNames.index(y)
        intercept = interceptMatrix[endNodeNumber]
        print("Intercept = ", intercept)
        coefficients = [x for x in coefficientMatrix[endNodeNumber] if x != 0]
        print("Coefficient = ", coefficients)
            
        output = debias_SEM_continious(X,coefficients,intercept,Vsim, strength)
        
        data_dbias[y] = output
    
    ## ------------------------------------ ##
    
    
    def modifyEdge(endNode,sensitiveVariable, strength):
        endNodeName =  columnNames[endNode]

        X = data_dbias[relationDict[endNodeName]].copy(deep=True)

        if(columnType[data_ip.columns.get_loc(endNodeName)] == True):
            print("--> Categorical")
            debias_categorical(X, endNodeName, sensitiveVariable, strength)
        else:
            print("--> Numeric")
            debias_continuous(X, endNodeName, sensitiveVariable, strength)

    
    ## ---------- Algo 19 - 25 ------------- ##
        
    data_dbias = data_ip.copy(deep=True)
    
    for v in topological_sort(edgeMatrixToFrontend(edgeMatrix)):
        if columnNames[v] in Vsim: #check the column is in Vsim
            print(columnNames[v])
            
            # Find sensitive variable
            sensitiveVariable = []
            strength = []
            for modifiedEdge in Edges_modified:
                # Node pointed by the modifieded edge
                if(v == modifiedEdge[1]):
                    sensitiveVariable.append(columnNames[modifiedEdge[0]])
                    strength.append(modifiedEdge[2])
            
            print(sensitiveVariable," ai= ", strength)
            modifyEdge(v,sensitiveVariable, strength) #Debias column with sensitive Variable
    
    ## ------------------------------------ ##        
            
    def DPD(v):
        #print("Type = ",type(v))
        #v = pd.Series(v)
        # Count occurrence of each element
        counts = Counter(v)
        
        # Calculate probabilities
        preds = {key: value/len(v) for key, value in counts.items()}
        
        return preds

    def get_prob(ip):
        if ip.shape[1] == 1:
            # Binary classification (1D array)
            #output = output.flatten()
            #print("-----> 1D")
            output = np.where(ip >= 0.5, 1, 0)
            output = output.reshape(-1,1).flatten()
            return pd.Series(output)
        else:
            # Multinomial classification (2D array)
            #print("-----> 2D")
            output = np.argmax(ip, axis=1)
            output = output.reshape(-1,1).flatten()
            return pd.Series(output)
    
    ## ---------- Rescaling - Algorithm 2 ------------- ##
    
    def rescale_categorical(original_data, prob_mat):
    
        #print("oirg type = ",type(original_data))
        lr = 0.1 #learning rate
        iteration = 0
        
        while (True):    

            #print("Iteration = ",iteration)

            #DPD - D[v]
            dist_ori = DPD(original_data)
            #print("dist_ori = ",dist_ori)


            #DPD - D_debias[v]
            dist_deb = DPD(get_prob(prob_mat))
            #print("dist_deb = ",dist_deb)


            diff = 0
            for i in dist_ori:
                if i in dist_deb:
                    diff = diff + abs((dist_ori[i] - dist_deb[i]) / dist_deb[i])
                else:
                    # Handle missing keys by assuming a value of zero in dist_deb
                    diff = diff + abs(dist_ori[i])
            #print("diff = ",diff)

            """
            if i in dist_deb:
                diff = diff + abs((dist_ori[i] - dist_deb[i]) / dist_deb[i])
            else:
                # Handle missing keys by assuming a value of zero in dist_deb
                diff = diff + abs(dist_ori[i])
            """
            
            
            scale_diff = 0
            for i in dist_ori:
                if i in dist_deb:
                    scale_diff = scale_diff + ((dist_ori[i] - dist_deb[i])/dist_deb[i])
                else:
                    # Handle missing keys by assuming a value of zero in dist_deb
                    scale_diff = scale_diff + (dist_ori[i])
            #print(scale_diff)


            scale_factor = 1 + lr * (scale_diff)


            prob_mat = np.dot(prob_mat,scale_factor)


            #newoutput = get_prob(prob_mat)


            # Calculate probabilities
            dist_deb = DPD(get_prob(prob_mat))
            #print("dist_deb = ",dist_deb)


            new_diff = 0
            for i in dist_ori:
                if i in dist_deb:
                    new_diff = new_diff + abs((dist_ori[i] - dist_deb[i])/dist_deb[i])
                else:
                    # Handle missing keys by assuming a value of zero in dist_deb
                    new_diff = new_diff + abs(dist_ori[i])
            #print("new_diff = ",new_diff)


            if(new_diff > diff or iteration > 50):
                #print("------> To Break")
                break

            iteration = iteration + 1
            #print("---------------------------")
        
        return get_prob(prob_mat)
    
    def rescale_continious(original_data, debiased_data):
    
        before_mean = original_data.mean()
        before_std = original_data.std()
        
        debias_mean = debiased_data.mean()
        debias_std = debiased_data.std()

        #  Rescale values for the simulated attributes
        numerical_dbias = before_mean + (debiased_data - debias_mean)/debias_std * before_std
        
        return numerical_dbias
    
    
    ## ------------------------------------ ## 
    
    ## ---------- Algo 27 - 37 ------------- ##
    for v in Vsim:
        print(v)
            
        y = v
        if(columnType[data_ip.columns.get_loc(y)] == True):
            print("--> Categorical")
            newoutput = rescale_categorical(data_ip[y], data_prob[y])
            data_dbias[y] = newoutput
            
        else:
            print("--> Numeric")
            newoutput = rescale_continious(data_ip[y], data_dbias[y])
            data_dbias[y] = newoutput
        
    ## ------------------------------------ ## 

    # Cross tabulation between GENDER and JOB
    CrosstabResult=pd.crosstab(index = data_ip['Gender'],columns=data_dbias['Job'])
    print("----------------")
    print(CrosstabResult)
    print("----------------")


          
    
    return data_dbias, CrosstabResult