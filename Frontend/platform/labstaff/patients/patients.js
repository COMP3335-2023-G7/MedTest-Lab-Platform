// Function to fetch patient data from the API
async function getPatientData() {
    try {
        const response = await fetch('http://localhost:6688/api/orders', {
            "credentials": "include",
        });
        const data = await response.json();
        console.log("API Response:", data); // Log the response for debugging
        return data.data;
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Function to initialize the user interface with patient data
async function initializeUI() {
    const patients = await getPatientData();
    var patientsContainer = document.getElementById("patientsContainer");
    patientsContainer.classList.add("flex"); // Use flex layout for the patient cards

    patients.forEach(function (patient) {
        var card = document.createElement("div");
        card.className = "card mr-4"; // Styling for each patient card

        var cardBody = document.createElement("div");
        cardBody.className = "card-body";

        var testCode = document.createElement("span");
        testCode.className = "tag tag-teal";
        testCode.textContent = patient.testCode;

        var patientName = document.createElement("h4");
        patientName.style.fontSize = "200%";
        patientName.innerHTML = "<b>" + patient.patientName + "</b>";

        var dob = document.createElement("h4");
        dob.innerHTML = "<b>Date of Birth</b> " + patient.patientBirthdate;

        var contactNumber = document.createElement("h4");
        contactNumber.innerHTML = "<b>Contact Number</b> " + patient.patientContact;

        var orderID = document.createElement("h4");
        orderID.innerHTML = "<b>Order ID</b> " + patient.orderId;

        var status = document.createElement("h4");
        status.innerHTML = "<b>Status</b> " + patient.status;

        var fillInResultsForm = document.createElement("form");
        fillInResultsForm.action = "fill_in_result.html";

        var fillInResultsButton = document.createElement("button");
        fillInResultsButton.className = "text-1xl px-4 py-2 tracking-wide text-white transition-colors duration-200 transform bg-gray-700 rounded-md hover:bg-gray-600 focus:outline-none focus:bg-gray-600";
        fillInResultsButton.textContent = "Fill in Results";

        // Store orderId in localStorage when the button is clicked
        fillInResultsButton.addEventListener("click", function() {
            localStorage.setItem("orderId", patient.orderId);
        });

        fillInResultsForm.appendChild(fillInResultsButton);

        cardBody.appendChild(testCode);
        cardBody.appendChild(document.createElement("br"));
        cardBody.appendChild(patientName);
        cardBody.appendChild(document.createElement("br"));
        cardBody.appendChild(dob);
        cardBody.appendChild(contactNumber);
        cardBody.appendChild(orderID);
        cardBody.appendChild(status);
        cardBody.appendChild(document.createElement("br"));
        cardBody.appendChild(fillInResultsForm);

        card.appendChild(cardBody);
        patientsContainer.appendChild(card);
    });
}

// Function to handle the submission of patient results
function handlePatientsResult(interpretation, reportingPathologist, orderId) {
    var data = new URLSearchParams();
    data.append('interpretation', interpretation);
    data.append('reportingPathologist', reportingPathologist);
    data.append('orderId', orderId);

    fetch('http://localhost:6688/api/results', {
        method: 'POST',
        credentials: 'include',
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: data
    })
    .then(response => response.json())
    .then(result => {
        console.log(result);
        if (result.message === "Result submitted successfully.") {
            alert("Result submitted successfully.");
            updateOrderStatus(orderId);
            localStorage.removeItem("orderId");
            window.location.href = "index.html";
        } else {
            alert("Error submitting result.");
            localStorage.removeItem("orderId");
        }
    })
    .catch(error => {
        console.error('Error submitting result:', error);
    });
}

function updateOrderStatus(orderId) {
    var data = new URLSearchParams();
    data.append('orderId', orderId);
    data.append('newStatus', "Completed");

    fetch('http://localhost:6688/api/orders/status', {
        method: 'PUT',
        credentials: 'include',
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: data
    })
    .then(response => response.json())
    .then(result => {
        console.log(result);
        if (result.message === "Order status updated successfully.") {
            alert("Order status updated successfully.");
            localStorage.removeItem("orderId");
            window.location.href = "index.html";
        } else {
            alert("Error updating order status.");
            localStorage.removeItem("orderId");
        }
    })
    .catch(error => {
        console.error('Error updating order status:', error);
    });
}

function handleResultInput() {
    var interpretation = document.getElementById("interpretation").value;
    var reportingPathologist = document.getElementById("reportingPathologist").value;
    var orderId = localStorage.getItem("orderId");
    
    handlePatientsResult(interpretation, reportingPathologist, orderId);
}


function generateReport() {

}

function generateReportURL() {
    
}
