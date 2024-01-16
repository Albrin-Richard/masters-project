//*****************  Source and Target List Populate *****************//

// Set the default selected option based on the 'columnNames' variable
// Replace 'defaultOption' with the index you want to select by default
var defaultOption = 0; // For example, to select the first option by default

// Get a reference to the <select> elements and the button
var sourceSelect = document.getElementById("sourceList");
var targetSelect = document.getElementById("targetList");

// Populate the <select> elements with options from the 'columnNames' variable
for (var i = 0; i < columnNames.length; i++) {
    var option = document.createElement("option");
    option.value = i; // You can set the value to something meaningful if needed
    option.textContent = columnNames[i];
    sourceSelect.appendChild(option.cloneNode(true));
    targetSelect.appendChild(option);
}

// Set default to the Source and Target <select> element 0th element
sourceSelect.selectedIndex = defaultOption;
targetSelect.selectedIndex = defaultOption;

 

// Initialize arrays to track added and modified edges
window.edgesAdded = [];
window.edgesModified = [];

// Variable to track if Debias is toggled
var isDebiasToggled = false;

//*****************  Refine Toggle button Functions *****************//
$(document).ready(function () {
    // Attach an event listener to the "Refine" radio button
    $('#refine').change(function () {
        if ($(this).prop('checked')) {

            isDebiasToggled = false;
            // Enable Direct and Reverse buttons
            $('#direct').prop('disabled', false);
            $('#reverse').prop('disabled', false);
            // Clear the edge tracking arrays when Debias is toggled off
            //edgesAdded = [];
            //edgesModified = [];
        } 
    });
});

//***************** Debias Toggle button Functions *****************//
$(document).ready(function () {
    // Attach an event listener to the "Debias" radio button
    $('#debias').change(function () {
        if ($(this).prop('checked')) {

            isDebiasToggled = true;
            // Disable Direct and Reverse buttons
            $('#direct').prop('disabled', true);
            $('#reverse').prop('disabled', true);
            
            // Replace this with code to get the edgeMatrix from your frontend
            //var edgeMatrix = window.edgeMatrix; // Implement this function

            // Serialize the array as JSON
            var edgeMatrixJSON = JSON.stringify(window.edgeMatrix);
            console.log('Edge matrix :', edgeMatrixJSON);

            var csrfToken = getCookie('csrftoken'); // Retrieve CSRF token

            // Send the edgeMatrix to the Django view using AJAX
            $.ajax({
                url: 'refined_edge_matrix/', // URL of your Django view
                method: 'POST',
                data: {
                    'edgeMatrix': edgeMatrixJSON,
                    'csrfmiddlewaretoken': csrfToken, // Include the CSRF token
                },
                success: function (response) {
                    console.log('Edge matrix sent successfully');
                    // Update the edgeMatrix and edgeWeightMatrix with the response
                    window.edgeMatrix = response.edge_matrix;
                    window.edgeWeightMatrix = response.edge_weight_matrix;

                    // Update edge weights in Cytoscape
                    cy.one('layoutstop', function () {
                        updateEdgeWeightsInCytoscape(window.edgeWeightMatrix);
                    });

                    // After updating all edge weights and re-adding edges, trigger a layout recalculation
                    cy.layout({ name: 'dagre' }).run();

                },
                error: function (xhr, status, error) {
                    console.error('Error sending edge matrix:', error);
                }
            });
        }
    });
});

function updateEdgeWeightsInCytoscape(edgeWeightMatrix) {
    /// Update weights for all edges
    cy.edges().forEach(function (edge) {
        var source = edge.source();
        var target = edge.target();
        var edgeWeight = edgeWeightMatrix[source.id().substring(1)][target.id().substring(1)];

        // Update the edge weight in Cytoscape
        edge.data('value', edgeWeight.toString());
    });

    // Remove all edges
    cy.edges().remove();

    // Add all edges back
    // Assuming you have a global variable window.edgeMatrix
    // Use your logic to add edges back based on edgeMatrix

    window.edgeMatrix.forEach(function (row, rowIndex) {
        row.forEach(function (value, colIndex) {
            if (value !== 0) {
                // Add the edge back
                cy.add({
                    group: 'edges',
                    data: {
                        source: 'n' + rowIndex,
                        target: 'n' + colIndex,
                        value: edgeWeightMatrix[rowIndex][colIndex].toString(),
                        direction: 'directed'  // Assuming all edges are directed
                    },
                });
            }
        });
    });
    console.log("Edges:", cy.edges().map(edge => edge.data()));

    // After updating all edge weights and re-adding edges, trigger a layout recalculation
    cy.layout({ name: 'dagre' }).run();
}

// Function to get cookie
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Search for the CSRF token name
            if (cookie.substring(0, name.length + 1) === name + '=') {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//***************** Function to detect Cycles in graph *****************//
function hasCycle(edgeMatrix, rowIndex, colIndex, operation) { 
    
    const numNodes = edgeMatrix.length;

    // Create a copy of the edgeMatrix to work with
    const edgeMatrixCopy = edgeMatrix.map(row => [...row]);
    
    if (operation === 'add'){
        edgeMatrixCopy[rowIndex][colIndex] = 1;
    } else if (operation === 'reverse') {
        edgeMatrixCopy[rowIndex][colIndex] = 0;
        edgeMatrixCopy[colIndex][rowIndex] = 1;
    } 
    
    // Convert all negative edge weights in the copy to 0
    for (let i = 0; i < numNodes; i++) {
        for (let j = 0; j < numNodes; j++) {
            if (edgeMatrixCopy[i][j] < 0) {
                edgeMatrixCopy[i][j] = 0;
            }
        }
    }

    function dfs(node, visited, stack) {
        visited[node] = true;
        stack[node] = true;

        for (let neighbor = 0; neighbor < numNodes; neighbor++) {
            if (edgeMatrixCopy[node][neighbor] > 0) {
                if (!visited[neighbor]) {
                    if (dfs(neighbor, visited, stack)) {
                        return true;
                    }
                } else if (stack[neighbor]) {
                    return true;
                }
            }
        }

        stack[node] = false;
        return false;
    }

    const visited = new Array(numNodes).fill(false);
    const stack = new Array(numNodes).fill(false);

    for (let node = 0; node < numNodes; node++) {
        if (!visited[node]) {
            if (dfs(node, visited, stack)) {
                return true; // Positive cycle detected
            }
        }
    }

    return false; // No positive cycles found
}

//*****************  Function to Add an edge *****************//
function createEdge(sourceValue, targetValue) {
    // Add your edge creation logic here using sourceValue and targetValue
    console.log("Creating edge from source: " + columnNames[sourceValue] + " to target: " + columnNames[targetValue]);

    // After reversing an edge, first, check for cycles
    if (!hasCycle(edgeMatrix, sourceValue, targetValue, 'add') && (edgeMatrix[sourceValue][targetValue] != 1)) {

        // Update the edgeMatrix to reverse the edge
        edgeMatrix[sourceValue][targetValue] = 1;

        // Add the reversed edge
        cy.add({
            group: 'edges',
            data: {
                source: 'n'+ sourceValue,
                target: 'n'+ targetValue,
                value: edgeWeightMatrix[sourceValue][targetValue].toString(),  // edge weight data
                direction: 'directed'
            },
            
        });

        // Add the reversed edge to edgesAdded only when Debias is toggled
        if (isDebiasToggled) {
            let edge = [parseInt(sourceValue), parseInt(targetValue)];
    
            if (!window.edgesAdded.some(e => e.toString() === edge.toString())) {
                window.edgesAdded.push(edge);
            }

            let matchingEdges = window.edgesModified.filter(e => JSON.stringify(e.slice(0, 2)) === JSON.stringify(edge));
            if (matchingEdges.length > 0) {
                console.log(`Match found in edgesModified: ${JSON.stringify(matchingEdges)}. Removing...`);
                window.edgesModified = window.edgesModified.filter(e => !matchingEdges.includes(e));
            }
        }

        // Refresh the Cytoscape-Dagre layout
        cy.layout({ name: 'dagre' }).run();

    } else {
        console.log('--> Cycle detected. Cannot add the edge.');  
    }

    console.log(`Edges Addes:`, edgesAdded);

    console.log(`edgesModified:`, edgesModified);

    // Print the updated edge matrix
    console.log('Updated Edge Matrix:');
    console.log(edgeMatrix);    

    console.log('Edges Added:');
    console.log(edgesAdded);

}

// Add a click event handler to the "create" button
document.getElementById('create').addEventListener('click', function() {
    
    /// Get the selected source and target values from the <select> lists
    var sourceValue = sourceSelect.value;
    var targetValue = targetSelect.value;

    // Perform the edge creation here, e.g., using the values from the <select> lists
    createEdge(sourceValue, targetValue);

});

//*****************  Function to Direct an edge *****************//
function directEdge(edge) {
    var edgeMatrix = window.edgeMatrix;
    var edgeWeightMatrix = window.edgeWeightMatrix;
    // Check if the edge is currently undirected (-1)
    if (edge.data('direction') === 'undirected') {
        
        // Get the current source and target nodes
        var sourceNode = edge.source();
        var targetNode = edge.target();

        // Direct the edge (change -1 to 1)
        var rowIndex = parseInt(sourceNode.id().substring(1));
        var colIndex = parseInt(targetNode.id().substring(1));

        // To direct an edge, first, check for cycles
        if (!hasCycle(edgeMatrix, rowIndex, colIndex, 'add')) {
            
            edgeMatrix[rowIndex][colIndex] = 1;

            // Update the style for the directed edge
            edge.style('line-color', '#9dbaea'); // Change line color
            edge.style('target-arrow-shape', 'triangle'); // Change arrow shape
            edge.style('target-arrow-color', '#9dbaea'); // Change arrow color
            edge.style('label', edgeWeightMatrix[rowIndex][colIndex].toString()); // Show edge value as label
            edge.data('direction', 'directed'); // Update the direction data

            // Refresh the Cytoscape-Dagre layout
            cy.layout({ name: 'dagre' }).run();

            // Print the updated edge matrix
            console.log('Updated Edge Matrix:');
            console.log(edgeMatrix);
        } else {
            console.log('--> Cycle detected. Cannot direct the edge.');
        }

        // Print the updated edge matrix
        console.log('Updated Edge Matrix:');
        console.log(edgeMatrix);
    }
}
// Add a click event handler to the "Direct" button
document.getElementById('direct').addEventListener('click', function() {
    
    // Code to execute when the button is clicked
    //console.log('Button clicked!'); // Print something in the console

    // Get the currently tapped edge
    var tappedEdge = cy.$(':selected');

    //console.log('Selected :');
    //console.log(tappedEdge.data())

    // Check if an edge is selected
    if (tappedEdge.length === 1 && tappedEdge.isEdge()) {
        // Direct the edge if it is undirected
        directEdge(tappedEdge);

    } else {
        console.log('Please select an edge to direct.');
    }
});

//*****************  Function to Reverse an edge *****************//
function reverseEdge(edge) {
    console.log('Reverse Edge :');
    
    var edgeMatrix = window.edgeMatrix;
    var edgeWeightMatrix = window.edgeWeightMatrix;

    // Check if the edge is currently directed (1)
    if (edge.data('direction') === 'directed') {
        
        // Get the current source and target nodes
        var sourceNode = edge.source();
        var targetNode = edge.target();

        // Get the corresponding row and column indices in the edgeMatrix
        var rowIndex = parseInt(sourceNode.id().substring(1));
        var colIndex = parseInt(targetNode.id().substring(1));

        // After reversing an edge, first, check for cycles
        if (!hasCycle(edgeMatrix, rowIndex, colIndex, 'reverse')) {

            // Update the edgeMatrix to reverse the edge
            edgeMatrix[rowIndex][colIndex] = 0;
            edgeMatrix[colIndex][rowIndex] = 1;

            // Remove the current edge
            cy.remove(edge);

            // Add the reversed edge
            cy.add({
                group: 'edges',
                data: {
                    source: targetNode.id(),
                    target: sourceNode.id(),
                    value: edge.data('value'),  // You can copy other data as well
                    direction: 'directed'
                },
                
            });

            // Refresh the Cytoscape-Dagre layout
            cy.layout({ name: 'dagre' }).run();

        } else {
            console.log('--> Cycle detected. Cannot reverse the edge.');  
        }

        // Print the updated edge matrix
        console.log('Updated Edge Matrix:');
        console.log(edgeMatrix);
        
    } else {
        console.log('--> Edge Undirected. Cannot reverse the edge.');  
    }
}

// Add a click event handler to the "Reverse Edge" button
document.getElementById('reverse').addEventListener('click', function () {
    // Get the currently tapped edge
    var tappedEdge = cy.$(':selected');

    // Check if an edge is selected
    if (tappedEdge.length === 1 && tappedEdge.isEdge()) {
        // Reverse the edge if it is directed and there's no cycle
        reverseEdge(tappedEdge);
    } else {
        console.log('Please select an edge to reverse');
    }
});

//***************** Function to delete an edge *****************//
function deleteEdge(edge) {
    var edgeMatrix = window.edgeMatrix;

    // Get the source and target node IDs
    var sourceId = edge.source().id();
    var targetId = edge.target().id();
    var rowIndex = parseInt(sourceId.substring(1));
    var colIndex = parseInt(targetId.substring(1));
    
    // Check if the edge exists (non-zero) before deleting it
    if (edgeMatrix[rowIndex][colIndex] !== 0) {
        edgeMatrix[rowIndex][colIndex] = 0; // Set edge weight to 0
        edge.data('direction', 'deleted'); // Mark the edge as deleted (for tracking purposes)

        // Remove the edge from the graph
        edge.remove();

        // Add the reversed edge to edgesAdded only when Debias is toggled
        if (isDebiasToggled) {
            let modifiedEdge = [parseInt(rowIndex), parseInt(colIndex), 0];

            if (!window.edgesModified.some(e => JSON.stringify(e) === JSON.stringify(modifiedEdge))) {
                window.edgesModified.push(modifiedEdge);
            }

            let matchingEdges = window.edgesAdded.filter(e => JSON.stringify(e) === JSON.stringify(modifiedEdge.slice(0, 2)) );
            if (matchingEdges.length > 0) {
                console.log(`Match found in edgesAdded: ${JSON.stringify(matchingEdges)}. Removing...`);
                window.edgesAdded = window.edgesAdded.filter(e => !matchingEdges.includes(e));
            }
        

        }


        console.log(`Edges Addes:`, edgesAdded);

        console.log(`edgesModified:`, edgesModified);

        // Print the updated edge matrix
        console.log('Updated Edge Matrix:');
        console.log(edgeMatrix);

        console.log('Edges Modified:');
        console.log(edgesModified);
        
    }
}

// Add a click event handler to the "Delete Edge" button
document.getElementById('delete').addEventListener('click', function() {
    // Get the currently tapped edge
    var tappedEdge = cy.$(':selected');

    // Check if an edge is selected
    if (tappedEdge.length === 1 && tappedEdge.isEdge()) {
        // Delete the edge
        deleteEdge(tappedEdge);
    } else {
        console.log('Please select an edge to delete.');
    }
});
