from django.shortcuts import render
from matplotlib.style import context
from django.http import JsonResponse
import json

# Create your views here.
from .models import DAGNode
from algorithms.pcDAG import debias_hiring_dataset, dataToDAG_PC, edgeMatrixToFrontend
from algorithms.edge_weight import getEdgeWeight
from algorithms.debias_dataset import dataset_debias
from .forms import PValueForm


data_encoded = None
columnNames = None # Define columnNames with an initial value
columnType = None

edgeMatrix = [] # Define edgeMatrix with an initial value
coefficientMatrix = None
interceptMatrix = None
edgeWeightMatrix = None # Define edgeWeightMatrix with an initial value
edgeWeightMatrix_transpose = None

# Data at the Begining of Page Refresh
def index(request): 


    if request.method == 'POST':
        form = PValueForm(request.POST)
        if form.is_valid():
            p_value = form.cleaned_data['inlineRadioOptions']
            
            # Get encoded dataset
            global data_encoded
            global columnNames
            global columnType
            
            data_encoded, columnNames, columnType = debias_hiring_dataset()
            
            # Edge Matrix
            global edgeMatrix
            edgeMatrix = dataToDAG_PC(p_value, data_encoded)
            
            # Edge Weight
            global edgeWeightMatrix
            _, _, edgeWeightMatrix = getEdgeWeight(data_encoded, columnType, edgeMatrix)
            edgeWeightMatrix_transpose = list(map(list, zip(*edgeWeightMatrix)))
    else:
        form = PValueForm()
        edgeWeightMatrix_transpose = []

    context = {
        'edge_matrix': edgeMatrixToFrontend(edgeMatrix),
        'edge_weight_matrix': edgeWeightMatrix_transpose,
        'column_names': columnNames,
        'form': form,
    }
    return render(request, 'dashboard/index.html', context)


def refined_edge_matrix(request):
    if request.method == 'POST':
        edge_matrix_json = request.POST.get('edgeMatrix')  # Retrieve as a JSON string
        
        try:
            edge_matrix = json.loads(edge_matrix_json)  # Parse the JSON string
            # Process the edgeMatrix in your Python code
            # You can access the edge_matrix variable here
            # ...
            print("Refined Edge matrix = ")
            print(edge_matrix)
            
            global edgeMatrix
            
            edgeMatrix = list(map(list, zip(*edge_matrix)))
            print("Edge matrix TRANS = ")
            print(edgeMatrix)
            
            # Get encoded dataset
            #data_encoded, _, columnType = debias_hiring_dataset()
            
            # Edge Weight
            global coefficientMatrix
            global interceptMatrix
            global edgeWeightMatrix
            
            coefficientMatrix, interceptMatrix, edgeWeightMatrix = getEdgeWeight(data_encoded, columnType, edgeMatrix)
            edgeWeightMatrix_transpose = list(map(list, zip(*edgeWeightMatrix)))
            
            print("Edge Weight matrix = ")
            print(edgeWeightMatrix_transpose)

            return JsonResponse({'success': True, 'edge_matrix': edgeMatrixToFrontend(edgeMatrix), 'edge_weight_matrix': edgeWeightMatrix_transpose, 'message': 'Edge matrix processed successfully'})
        except json.JSONDecodeError as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'message': 'Invalid request'}, status=400)

def evaluate_bias(request):
    if request.method == 'POST':
        bias_variable_value = request.POST.get('bias_variable')
        target_variable_value = request.POST.get('target_variable')
        edgesAdded_value = request.POST.get('edgesAdded')
        edgesModified_value = request.POST.get('edgesModified')
        
        edgesAdded = json.loads(edgesAdded_value)  # Parse the JSON string
        edgesModified = json.loads(edgesModified_value)  # Parse the JSON string
        
        data_dbias, CrosstabResult = dataset_debias(data_encoded, columnType, edgeMatrix, coefficientMatrix, interceptMatrix, edgeWeightMatrix, edgesAdded, edgesModified)

        f_job =  ((CrosstabResult[1][0]/1588) *100)
        m_job =  ((CrosstabResult[1][1]/2412) *100)
        
        # Perform actions based on the selected values from the dropdowns
        # For example, create a JSON response (replace this with your logic)
        response_data = {
            'message': 'Bias Evaluation Completed!',
            'result': {
                'bias_variable_value': bias_variable_value,
                'target_variable_value': target_variable_value,
                'edgesAdded': edgesAdded_value,
                'edgesModified': edgesModified_value,
                'Female Percent' : f_job ,
                'Male Percent' :  m_job,
                'Percent diff' : abs(round(m_job - f_job))
                
                # Add more data as needed
            }
        }

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid Request'})  # Handling unexpected POST requests or GET requests







def dag_view(request):
    
    
    dag_nodes = [{
        'id': 'node1',
        'name': 'Node 1',
        'parent': None,  # The root node (no parent)
    },
    {
        'id': 'node2',
        'name': 'Node 2',
        'parent': 'node1',  # Node 2 is a child of Node 1
    },
    {
        'id': 'node3',
        'name': 'Node 3',
        'parent': 'node1',  # Node 3 is also a child of Node 1
    },
    # Add more nodes as needed
    ]
    return render(request, 'dag_template.html', {'dag_nodes': dag_nodes})