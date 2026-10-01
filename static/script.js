let recognition;

const micButton =
    document.getElementById("micButton");

const voiceStatus =
    document.getElementById("voiceStatus");

const voiceText =
    document.getElementById("voiceText");


// Check browser support

if ("webkitSpeechRecognition" in window) {

    recognition =
        new webkitSpeechRecognition();

    recognition.lang = "en-IN";

    recognition.continuous = false;

    recognition.interimResults = false;


    recognition.onstart = function () {

        voiceStatus.innerText =
            "Listening... Speak now.";

        micButton.innerText =
            "🔴 Listening...";

    };


    recognition.onresult = function (event) {

        const text =
            event.results[0][0].transcript;

        voiceText.innerText =
            text;

        processCommand(text);

    };


    recognition.onerror = function (event) {

        voiceStatus.innerText =
            "Voice error: " + event.error;

        micButton.innerText =
            "🎤 Start Speaking";

    };


    recognition.onend = function () {

        voiceStatus.innerText =
            "Voice recognition stopped.";

        micButton.innerText =
            "🎤 Start Speaking";

    };


} else {

    voiceStatus.innerText =
        "Speech recognition is not supported in this browser.";

}


// Start microphone

micButton.addEventListener("click", function () {

    if (recognition) {
        recognition.start();
    }

});


// Send voice command to Flask

async function processCommand(command) {

    document.getElementById("response").innerText =
        "Processing...";


    try {

        const result = await fetch("/api/command", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                command: command
            })

        });


        const data =
            await result.json();


        document.getElementById("response").innerText =
            data.response;


        // Speak response

        speak(data.response);


        // Display books if returned

        if (data.books) {

            displayBooks(data.books);

        }

    } catch (error) {

        document.getElementById("response").innerText =
            "Unable to connect to server.";

    }

}


// Text-to-Speech

function speak(text) {

    if ("speechSynthesis" in window) {

        const speech =
            new SpeechSynthesisUtterance(text);

        speech.lang = "en-IN";

        speech.rate = 1;

        speech.pitch = 1;

        window.speechSynthesis.speak(speech);

    }

}


// Search books

async function searchBooks() {

    const search =
        document.getElementById("searchInput").value;


    try {

        const result =
            await fetch(
                "/api/books?search=" +
                encodeURIComponent(search)
            );


        const books =
            await result.json();


        displayBooks(books);


    } catch (error) {

        document.getElementById("response").innerText =
            "Unable to search books.";

    }

}


// Display books

function displayBooks(books) {

    const container =
        document.getElementById("bookContainer");


    container.innerHTML = "";


    if (!books.length) {

        container.innerHTML =
            "<p>No books found.</p>";

        return;

    }


    books.forEach(function(book) {

        const status =
            book.available_copies > 0
            ? "Available"
            : "Not Available";


        const card =
            document.createElement("div");


        card.className =
            "book-card";


        card.innerHTML = `

            <h3>${book.title}</h3>

            <p>
                <strong>Author:</strong>
                ${book.author}
            </p>

            <p>
                <strong>Category:</strong>
                ${book.category}
            </p>

            <p>
                <strong>Copies:</strong>
                ${book.available_copies}
                /
                ${book.total_copies}
            </p>

            <p class="${
                book.available_copies > 0
                ? "available"
                : "unavailable"
            }">

                ${status}

            </p>
        `;


        container.appendChild(card);

    });

}


// Load issued books

async function loadIssuedBooks() {

    try {

        const result =
            await fetch("/api/issued");


        const data =
            await result.json();


        const container =
            document.getElementById("issuedContainer");


        if (!data.length) {

            container.innerHTML =
                "<p>No issued books.</p>";

            return;

        }


        let html = `

            <table>

                <tr>
                    <th>Student</th>
                    <th>Book</th>
                    <th>Issue Date</th>
                    <th>Due Date</th>
                    <th>Status</th>
                </tr>
        `;


        data.forEach(function(item) {

            html += `

                <tr>

                    <td>
                        ${item.name}
                        <br>
                        ${item.student_id}
                    </td>

                    <td>
                        ${item.title}
                    </td>

                    <td>
                        ${item.issue_date}
                    </td>

                    <td>
                        ${item.due_date}
                    </td>

                    <td>
                        ${item.status}
                    </td>

                </tr>

            `;

        });


        html += "</table>";


        container.innerHTML =
            html;


    } catch (error) {

        document.getElementById("issuedContainer")
            .innerHTML =
            "<p>Unable to load issued books.</p>";

    }

}


// Load books when page opens

window.onload = function() {

    searchBooks();

};
