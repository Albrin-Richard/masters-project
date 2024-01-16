

window.addEventListener('DOMContentLoaded', function(){
        
    // Your edge matrix and column names

    // Your JavaScript code in a separate .js file
    console.log(edgeMatrix); // Access the edge matrix from your Python view
   

    var cy = window.cy = cytoscape({
        container: document.getElementById('cy'),

        // User interaction options
        userZoomingEnabled: true,   // Allow zooming
        userPanningEnabled: true,   // Allow panning
        boxSelectionEnabled: true,  // Enable box selection
        autounselectify: false,     // Enable manual unselecting of elements

        layout: {
        name: 'dagre', // or any other layout you prefe
        nodeSep: 30, // The separation between adjacent nodes in the same rank
        edgeSep: 10, // The separation between adjacent edges in the same rank
        rankSep: 50, // The separation between each rank in the layout
        rankDir: 'LR', // The direction of the layout ('TB', 'BT', 'LR', or 'RL')
        spacingFactor: 1.5, // A positive value which adjusts spacing between nodes
        // Set a fixed height for the graph
        height: 800 // Set the desired height of the DAG
        },

        style: [
        {
            selector: 'node',

            style: {
            'background-color': '#11479e',
            'shape': 'roundrectangle',
            'border-width': '2px',
            'border-color': '#ffffff',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '12px',     // Adjust the font size as needed
            'color': '#ffffff',
            'text-wrap': 'wrap',
            'text-max-width': '190px',
            'min-width': '80px',     /* Minimum width */
            'max-width': '200px',    /* Maximum width */
            'width': 'label',
            'height': '40px',
            'label': 'data(name)'
            }
        },

        {
            selector: 'edge',

            style: {
                'width': 4, // Set the edge width
                'curve-style': 'bezier', // Set the curve style
                'font-size': 12, // Set the font size of the label
                'color': '#000000' // Label text color
            }
        },
        
        {
            selector: 'edge[direction = "directed"]',
            style: {
                'line-color': '#9dbaea', // Set the edge line color for directed edges
                'target-arrow-shape': 'triangle', // Set the arrow shape for directed edges
                'target-arrow-color': '#9dbaea', // Set the arrow color for directed edges
                'label': 'data(value)', // Show edge value as label for directed edges
            }
        },
        
        {
            selector: 'edge[direction = "undirected"]',
            style: {
                'line-color': '#888888', // Set the edge line color for undirected edges (grey)
                'target-arrow-shape': 'none', // Remove arrowheads for undirected edges
                'source-arrow-shape': 'none', // Remove arrowheads for undirected edges
            }
        }
        ],

        elements: {
            nodes: columnNames.map(function (name, index) {
                return { data: { id: 'n' + index, name: name } };
            }),
            edges: edgeMatrix.reduce(function (edges, row, rowIndex) {
                row.forEach(function (value, colIndex) {
                    if (value !== 0) {
                        if (value === -1) {
                            // Create undirected edges 
                            edges.push({ data: { source: 'n' + rowIndex, target: 'n' + colIndex, value: edgeWeightMatrix[rowIndex][colIndex].toString(), direction: 'undirected' } });
                        
                        } else {
                            // Create directed edge
                            edges.push({ data: { source: 'n' + rowIndex, target: 'n' + colIndex, value: edgeWeightMatrix[rowIndex][colIndex].toString(), direction: 'directed' } });
                        }
                    }
                });
                return edges;
                }, [])
            }

    });

    // Calculate the width of the label text
    cy.nodes().forEach(function(node) {
        const label = node.data('name');
        const labelWidth = label.length * 8; // Adjust the multiplier based on font size and style
    
        // Ensure the calculated width is within the allowed range
        if (labelWidth < 80) {
        node.style('width', '80px'); // Set to minimum width
        } else if (labelWidth > 200) {
        node.style('width', '200px'); // Set to maximum width
        } else {
        node.style('width', labelWidth + 'px'); // Set to calculated width
        }
    });

    // Add a tap event handler to nodes
    cy.on('tap', 'node', function (event) {
        var node = event.target;
        
        // Reset opacity for all elements
        cy.elements().style('opacity', 0.5);

        // Highlight the clicked node, its outbound edges, and target nodes
        node.style('opacity', 1);
        node.outgoers().style('opacity', 1);

        // Print outbound edges and target nodes to the console
        console.log("Current Node:", node.data());
        console.log("Outbound Edges:", node.outgoers('edge').map(edge => edge.data()));
        console.log("Target Nodes:", node.outgoers('node').map(targetNode => targetNode.data()));
    });

    // Add a tap event handler to edges
    cy.on('tap', 'edge', function (event) {
        var edge = event.target;
        var fromNode = edge.source();
        var toNode = edge.target();
        
        // Reset opacity for all elements
        cy.elements().style('opacity', 0.5);


        // Highlight the clicked edges, from node, and target nodes
        edge.style('opacity', 1);
        fromNode.style('opacity', 1);
        toNode.style('opacity', 1);

        // Print the clicked edges from node, and target nodes to the console
        console.log("Clicked Edge:", edge.data());
        console.log("From Node:", fromNode.data());
        console.log("Target Node:", toNode.data());
    });

    // Add a tap event handler to the entire graph to reset opacity when clicking outside nodes and edges
    cy.on('tap', function (event) {
        var target = event.target;
        if (target === cy) {
            cy.elements().style('opacity', 1); // Reset opacity for all elements
        }

    });

    // Print nodes and edges to the console
    console.log("Nodes:", cy.nodes().map(node => node.data()));
    console.log("Edges:", cy.edges().map(edge => edge.data()));

    
    // You can access edgeMatrix from other scripts by attaching it to the global object
    window.edgeMatrix = edgeMatrix;
    window.edgeWeightMatrix = edgeWeightMatrix;

    


    
});


/*
// Get the button element by its id
var directButton = document.getElementById('direct');

function directEdge(edge) {
    // Check if the edge is currently undirected (-1)
    if (edge.data('direction') === 'undirected') {
        // Direct the edge (change -1 to 1)
        var rowIndex = parseInt(edge.source().id().substring(1));
        var colIndex = parseInt(edge.target().id().substring(1));
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
    }
}

// Add a click event listener to the button
directButton.addEventListener('click', function () {
    // Code to execute when the button is clicked
    console.log('Button clicked!'); // Print something in the console

    // Get the currently tapped edge
    var tappedEdge = cy.$(':selected');

    console.log('Selected :');
    console.log(tappedEdge.data('direction'))

    // Check if an edge is selected
    if (tappedEdge.length === 1 && tappedEdge.isEdge()) {
        // Direct the edge if it is undirected
        directEdge(tappedEdge);
    }
});
    
*/

