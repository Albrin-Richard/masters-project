/*****************  Source and Target List Populate *****************/

// Set the default selected option based on the 'columnNames' variable
// Replace 'defaultOption' with the index you want to select by default
var defaultOption = 0; // For example, to select the first option by default

// Get a reference to the <select> elements and the button
var biasVariableSelect = document.getElementById("bias_variable");
var targetVariableSelect = document.getElementById("target_variable");

// Populate the <select> elements with options from the 'columnNames' variable
for (var i = 0; i < columnNames.length; i++) {
    var option = document.createElement("option");
    option.value = i; // You can set the value to something meaningful if needed
    option.textContent = columnNames[i];
    biasVariableSelect.appendChild(option.cloneNode(true));
    targetVariableSelect.appendChild(option);
}

// Set default to the Source and Target <select> element 0th element
biasVariableSelect.selectedIndex = defaultOption;
targetVariableSelect.selectedIndex = columnNames.length - 1;

 

//Evaluate Bias
document.getElementById('evaluateBiasForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Fetch form data
    var formData = new FormData(this);

    // Access selected values of target_variable and bias_variable
    var biasVariable = document.getElementById('bias_variable').value;
    var targetVariable = document.getElementById('target_variable').value;

    // Append target_variable and bias_variable values to the form data
    formData.append('bias_variable', biasVariable);
    formData.append('target_variable', targetVariable);
    

    // Append target_variable and bias_variable values to the form data
    formData.append('target_variable', targetVariable);
    formData.append('bias_variable', biasVariable);

    // Append edgesAdded and edgesModified to the form data
    formData.append('edgesAdded', JSON.stringify(window.edgesAdded));
    formData.append('edgesModified', JSON.stringify(window.edgesModified));

    // Send form data asynchronously using AJAX
    fetch(this.action, {
        method: this.method,
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Process JSON response and display in the page
        var jsonResponseDiv = document.getElementById('jsonResponse');
        // Replace this example with your own logic to handle and display the JSON response
        jsonResponseDiv.innerHTML = JSON.stringify(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
});


// Plotly Model Metrics bar chart code
var model_bar1 = {
    x: [0.7, 0.7],
    y: ['Accuracy', 'F1'],
    name: 'Debiased',
    type: 'bar',
    orientation: 'h'
};

var model_bar2 = {
    x: [0.8, 0.8],
    y: ['Accuracy', 'F1'],
    name: 'Baseline',
    type: 'bar',
    orientation: 'h'
};

var model_data = [model_bar1, model_bar2];

var model_layout = {
    
    barmode: 'group',
    margin: {
        l: 20,
        r: 0,
        b: 0,
        t: 0  

    },
    legend: {
        orientation: 'h',
        yanchor: -0.5
      }
};

const config = {
    displayModeBar: false, // this is the line that hides the bar.
  };
  
Plotly.newPlot('mlMetricsDiv', model_data, model_layout, config);

// Data Distortion gauge
var dataDistortion_data = [
    {
      domain: { x: [0, 1], y: [0, 1] },
      value: 6,
      type: "indicator",
      mode: "gauge+number",
      delta: { reference: 400 },
      gauge: { axis: { range: [null, 25] } }
    }
  ];
  
  var layout = {
        height: 200,
        margin: {
            l: 20,
            r: 0,
            b: 0,
            t: 0  
        },
};
  Plotly.newPlot('dataDistortionDiv', dataDistortion_data, layout, config);
  
