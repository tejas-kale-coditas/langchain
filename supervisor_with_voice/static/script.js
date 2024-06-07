// const synth = window.speechSynthesis;

// const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
// recognition.continuous = false;
// recognition.lang = "en-US";
// recognition.interimResults = false;
// recognition.maxAlternatives = 1;

// const diagnostic = document.querySelector(".output");
// const log = document.querySelector(".log");
// const startButton = document.getElementById("startButton");

// let voices = [];

// function populateVoiceList() {
//     voices = synth.getVoices().sort((a, b) => a.name.localeCompare(b.name));
//     // Optional: handle voice selection if needed
// }

// populateVoiceList();

// if (speechSynthesis.onvoiceschanged !== undefined) {
//     speechSynthesis.onvoiceschanged = populateVoiceList;
// }

// function speak(text) {
//     console.log('speakTheText' + text)
//     if (synth.speaking) {
//         console.error("speechSynthesis.speaking");
//         return;
//     }

//     if (text !== "") {
//         const utterThis = new SpeechSynthesisUtterance(text);

//         utterThis.onend = function (event) {
//             console.log("SpeechSynthesisUtterance.onend");
//         };

//         utterThis.onerror = function (event) {
//             console.error("SpeechSynthesisUtterance.onerror");
//         };

//         // Optional: handle selected voice
//         if (voices.length > 0) {
//             utterThis.voice = voices[0]; // Default to first voice
//         }

//         synth.speak(utterThis);
//     }
// }

// startButton.onclick = () => {
//     startListening();
// };

// function startListening() {
//     try {
//         recognition.start();
//         diagnostic.textContent = "Listening...";
//         console.log("Ready to receive a speech command.");
//     } catch (error) {
//         console.log("Error starting recognition: ", error);
//     }
// }

// recognition.onresult = (event) => {
//     const transcript = event.results[0][0].transcript;
//     diagnostic.textContent = `Result received: ${transcript}`;
//     const logEntry = document.createElement("p");
//     logEntry.textContent = transcript;
//     logEntry.classList.add("log-entry");
//     log.appendChild(logEntry);
//     sendTranscript(transcript);
// };

// recognition.onspeechend = () => {
//     recognition.stop();
//     diagnostic.textContent = "Speech recognition has stopped.";
// };

// recognition.onerror = (event) => {
//     diagnostic.textContent = `Error occurred in recognition: ${event.error}`;
// };

// function sendTranscript(transcript) {
//     fetch('/process_speech', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({ transcript })
//     })
//     .then(response => response.json())
//     .then(data => {
//         const logEntry = document.createElement("p");
//         logEntry.textContent = `Response: ${data.response}`;
//         logEntry.classList.add("log-entry");
//         log.appendChild(logEntry);
//         speak(data.response);
//     })
//     .catch(error => {
//         console.error('Error:', error);
//     });
// }
// ========================
const synth = window.speechSynthesis;

const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.continuous = false;
recognition.lang = "en-US";
recognition.interimResults = false;
recognition.maxAlternatives = 1;

const diagnostic = document.querySelector(".output");
const log = document.querySelector(".log");
const startButton = document.getElementById("startButton");

let voices = [];
let speechQueue = [];
let isSpeaking = false;

function populateVoiceList() {
    voices = synth.getVoices().sort((a, b) => a.name.localeCompare(b.name));
}

populateVoiceList();

if (speechSynthesis.onvoiceschanged !== undefined) {
    speechSynthesis.onvoiceschanged = populateVoiceList;
}

function speak(text) {
    console.log('speakTheText: ' + text);
    if (text !== "") {
        const utterThis = new SpeechSynthesisUtterance(text);
        console.log('utterThis obj: '+ utterThis)

        utterThis.onend = function (event) {
            console.log("SpeechSynthesisUtterance.onend");
            isSpeaking = false;
            if (speechQueue.length > 0) {
                speak(speechQueue.shift());
            }
        };

        utterThis.onerror = function (event) {
            console.error("SpeechSynthesisUtterance.onerror");
            isSpeaking = false;
        };

        // Optional: handle selected voice
        if (voices.length > 0) {
            utterThis.voice = voices[4]; 
        }

        isSpeaking = true;
        synth.speak(utterThis);
    }
}

startButton.onclick = () => {
    startListening();
};

function startListening() {
    try {
        recognition.start();
        diagnostic.textContent = "Listening...";
        console.log("Ready to receive a speech command.");
    } catch (error) {
        console.log("Error starting recognition: ", error);
    }
}

recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    diagnostic.textContent = `Result received: ${transcript}`;
    const logEntry = document.createElement("p");
    logEntry.textContent = transcript;
    logEntry.classList.add("log-entry");
    log.appendChild(logEntry);
    sendTranscript(transcript);
};

recognition.onspeechend = () => {
    recognition.stop();
    diagnostic.textContent = "Speech recognition has stopped.";
};

recognition.onerror = (event) => {
    diagnostic.textContent = `Error occurred in recognition: ${event.error}`;
};

function sendTranscript(transcript) {
    fetch('/process_speech', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ transcript })
    })
    .then(response => response.json())
    .then(data => {
        const logEntry = document.createElement("p");
        logEntry.textContent = `Response: ${data.response}`;
        logEntry.classList.add("log-entry");
        log.appendChild(logEntry);
        // speak(data.response);
        const url = '/audio/' + data.file;
        const audio = new Audio(url);
        audio.play();
        audio.onended = () => {
            startButton.click();
        };
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
