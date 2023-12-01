async function getTestData() {
    try {
        const response = await fetch('http://pi.bebop404.com:6688/api/tests');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        if (data.message === "Tests retrieved successfully.") {
            return data.data;
        } else {
            console.error('Tests were not retrieved:', data.message);
        }
    } catch (error) {
        console.error('There has been a problem with your fetch operation:', error);
    }
}

async function initializeTestsUI() {
    const tests = await getTestData();
    console.log("Tests:", tests);
    if (!tests) return;

    var testsContainer = document.getElementById("testsContainer");
    testsContainer.classList.add("flex"); // Use flex layout for the test cards

    tests.forEach(function (test) {
        var card = document.createElement("div");
        card.className = "card mx-4 mb-4"; // Styling for each test card

        var cardBody = document.createElement("div");
        cardBody.className = "card-body";

        var testIdSpan = document.createElement("span");
        testIdSpan.className = "tag tag-teal";
        testIdSpan.textContent = test.testId;

        var testName = document.createElement("h4");
        testName.className = "text-2xl mt-2";
        testName.innerHTML = "<b>" + test.name + "</b>";

        var testCost = document.createElement("h4");
        testCost.innerHTML = "<b>Amount (HKD):</b> " + test.cost;

        var testDescription = document.createElement("p");
        testDescription.className = "mt-2";
        testDescription.textContent = test.description;


        var bookingForm = document.createElement("form");
        bookingForm.action = "booking_test.html";

        var bookingButton = document.createElement("button");
        bookingButton.className = "text-1xl px-4 py-2 tracking-wide text-white transition-colors duration-200 transform bg-gray-700 rounded-md hover:bg-gray-600 focus:outline-none focus:bg-gray-600";
        bookingButton.textContent = "Booking";

        // Store orderId in localStorage when the button is clicked
        bookingButton.addEventListener("click", function() {
            localStorage.setItem("testCode", test.testId);
        });

        bookingForm.appendChild(bookingButton);

        // Append all elements to the card body
        cardBody.appendChild(testIdSpan);
        cardBody.appendChild(document.createElement("br"));
        cardBody.appendChild(testName);
        cardBody.appendChild(testCost);
        cardBody.appendChild(document.createElement("br"));
        cardBody.appendChild(testDescription);
        cardBody.appendChild(bookingForm);

        // Append card body to card
        card.appendChild(cardBody);

        // Append card to the container
        testsContainer.appendChild(card);
    });
}
