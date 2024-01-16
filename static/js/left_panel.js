/*******************  To Populate column List *******************/

// Get a reference to the <ul> columnList element
var columnList = document.getElementById("columnList");

// Populate the <ul> columnList with items from the 'columnNames' variable
for (var i = 0; i < columnNames.length; i++) {
    var columnName = columnNames[i];
    var li = document.createElement("li");
    li.className = "list-group-item";
    li.textContent = columnName;
    columnList.appendChild(li);

}