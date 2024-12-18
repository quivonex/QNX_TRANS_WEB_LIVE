

// document.addEventListener('DOMContentLoaded', function () {
//     var branchField = document.querySelector('#{{ form.branch.id_for_label }}');
//     if (branchField) {
//         branchField.disabled = true;
//     }
// });



let selectedRow = null; // To keep track of the row being edited

function addToList() {

    const id = 0;
    const description = document.getElementById('description').value;
    const quantity = document.getElementById('quantity').value;
    const actualWeight = document.getElementById('actual_weight').value;
    const chargedWeight = document.getElementById('charged_weight').value;
    const unitType = document.getElementById('unit_type').value;
    const rate = document.getElementById('rate').value;
    const challanNo = document.getElementById('challan_no').value;
    const invValue = document.getElementById('inv_value').value;
    const eWayBillNo = document.getElementById('e_way_bill_no').value;

    if (!description || !quantity || !actualWeight || !chargedWeight || !unitType || !rate || !challanNo || !invValue || !eWayBillNo) {
        alert("Please fill in all fields.");
        return;
    }

    const table = document.getElementById('item-list').getElementsByTagName('tbody')[0];
    const newRow = selectedRow == null ? table.insertRow() : selectedRow;

    if (selectedRow == null) { // If no row is selected, add a new row
        newRow.innerHTML = `
                <td>0</td>
                <td>${description}</td>
                <td>${quantity}</td>
                <td>${actualWeight}</td>
                <td>${chargedWeight}</td>
                <td>${unitType}</td>
                <td>${rate}</td>
                <td>${challanNo}</td>
                <td>${invValue}</td>
                <td>${eWayBillNo}</td>
                <td>
                    <button type="button" onclick="editItem(this)" style="padding: 2px 4px;">Edit</button>
                    <button type="button" class="remove-button" onclick="removeItem(this)" style="padding: 2px 4px;">Remove</button>
                </td>
            `;
    } else { // If a row is selected, update the selected row's data
        newRow.cells[1].innerHTML = descriptionText;
        newRow.cells[2].innerHTML = quantity;
        newRow.cells[3].innerHTML = actualWeight;
        newRow.cells[4].innerHTML = chargedWeight;
        newRow.cells[5].innerHTML = unitType;
        newRow.cells[6].innerHTML = rate;
        newRow.cells[7].innerHTML = challanNo;
        newRow.cells[8].innerHTML = invValue;
        newRow.cells[9].innerHTML = eWayBillNo;

        // Reset selectedRow and hide the update button
        selectedRow = null;
        document.getElementById('updateButton').style.display = 'none';
        document.getElementById('addButton').style.display = 'inline-block';
    }

    clearFields(); // Clear input fields after adding or updating
    updateSerializedTableData(); // Update the hidden input with serialized data
}

function updateItem() {
    if (selectedRow) {

        selectedRow.cells[1].innerHTML = document.getElementById("description").value;
        selectedRow.cells[2].innerHTML = document.getElementById("quantity").value;
        selectedRow.cells[3].innerHTML = document.getElementById("actual_weight").value;
        selectedRow.cells[4].innerHTML = document.getElementById("charged_weight").value;
        selectedRow.cells[5].innerHTML = document.getElementById("unit_type").value;
        selectedRow.cells[6].innerHTML = document.getElementById("rate").value;
        selectedRow.cells[7].innerHTML = document.getElementById("challan_no").value;
        selectedRow.cells[8].innerHTML = document.getElementById("inv_value").value;
        selectedRow.cells[9].innerHTML = document.getElementById("e_way_bill_no").value;

        // Reset selectedRow and hide the update button
        selectedRow = null;
        document.getElementById('updateButton').style.display = 'none';
        document.getElementById('addButton').style.display = 'inline-block';
    }
    clearFields(); // Clear input fields after adding or updating
    updateSerializedTableData(); // Update the hidden input with serialized data
}

function editItem(button) {
    const row = button.parentNode.parentNode;
    document.getElementById('description').value = row.cells[1].innerHTML;
    document.getElementById('quantity').value = row.cells[2].innerHTML;
    document.getElementById('actual_weight').value = row.cells[3].innerHTML;
    document.getElementById('charged_weight').value = row.cells[4].innerHTML;
    document.getElementById('unit_type').value = row.cells[5].innerHTML;
    document.getElementById('rate').value = row.cells[6].innerHTML;
    document.getElementById('challan_no').value = row.cells[7].innerHTML;
    document.getElementById('inv_value').value = row.cells[8].innerHTML;
    document.getElementById('e_way_bill_no').value = row.cells[9].innerHTML;

    selectedRow = row;
    document.getElementById('updateButton').style.display = 'inline-block';
    document.getElementById('addButton').style.display = 'none';
}

function removeItem(button) {
    if (confirm('Are you sure you want to remove this item?')) {
        const row = button.parentNode.parentNode;
        const itemId = row.cells[0].innerHTML;

        if (itemId == 0) {
            // Remove row from the DOM
            row.parentNode.removeChild(row);
            updateSerializedTableData(); // Update hidden input after removing
        } else {
            // Perform AJAX request to delete the item
            const deleteUrl = `/lr_booking/delete_lr_booking_description/${itemId}/`;

            fetch(deleteUrl, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
                .then(response => {
                    if (response.ok) {
                        // Remove row from the DOM
                        row.parentNode.removeChild(row);
                        updateSerializedTableData(); // Update hidden input after removing
                    } else {
                        alert('Failed to delete item. Please try again.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred. Please try again.');
                });
        }
    }
}

// Helper function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function clearFields() {
    document.getElementById('description').value = '';
    document.getElementById('quantity').value = '';
    document.getElementById('actual_weight').value = '';
    document.getElementById('charged_weight').value = '';
    document.getElementById('unit_type').value = '';
    document.getElementById('rate').value = '';
    document.getElementById('challan_no').value = '';
    document.getElementById('inv_value').value = '';
    document.getElementById('e_way_bill_no').value = '';
}



function updateSerializedTableData() {
    const table = document.getElementById('item-list');
    const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
    const tableData = [];
    console.log("reached to this statement");

    for (let row of rows) {
        const cells = row.getElementsByTagName('td');
        console.log(cells[0].innerHTML);
        console.log(row.getElementsByTagName('td'));

        tableData.push({
            id: cells[0].innerHTML,
            description: cells[1].innerHTML,
            quantity: cells[2].innerHTML,
            actual_weight: cells[3].innerHTML,
            charged_weight: cells[4].innerHTML,
            unit_type: cells[5].innerHTML,
            rate: cells[6].innerHTML,
            challan_no: cells[7].innerHTML,
            inv_value: cells[8].innerHTML,
            e_way_bill_no: cells[9].innerHTML,
        });
    }

    document.getElementById('serialized_table_data').value = JSON.stringify(tableData);
}


