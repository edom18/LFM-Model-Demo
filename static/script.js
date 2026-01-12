
let stream = null;
let isRunning = false;
let video = null;
let canvas = null;
let promptInput = null;
let toggleButton = null;
let logContainer = null;

document.addEventListener('DOMContentLoaded', () => {
    video = document.getElementById('camera-view');
    canvas = document.getElementById('capture-canvas');
    promptInput = document.getElementById('prompt-input');
    toggleButton = document.getElementById('toggle-btn');
    logContainer = document.getElementById('log-container');

    toggleButton.addEventListener('click', toggleAnalysis);

    // Initialize camera
    startCamera();
});

async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (err) {
        console.error("Error accessing camera:", err);
        addLog("Error accessing camera: " + err.message);
    }
}

function toggleAnalysis() {
    if (isRunning) {
        stopAnalysis();
    } else {
        startAnalysis();
    }
}

function startAnalysis() {
    isRunning = true;
    toggleButton.textContent = "停止";
    toggleButton.classList.add('stop');
    promptInput.disabled = true;
    
    analyzeLoop();
}

function stopAnalysis() {
    isRunning = false;
    toggleButton.textContent = "開始";
    toggleButton.classList.remove('stop');
    promptInput.disabled = false;
}

async function analyzeLoop() {
    if (!isRunning) return;

    try {
        // Capture frame
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert to blob
        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.8));
        const customPrompt = promptInput.value || "Describe this image";

        // Create form data
        const formData = new FormData();
        formData.append('image', blob, 'capture.jpg');
        formData.append('prompt', customPrompt);

        // Send request
        const startTime = new Date();
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        
        // Log result
        addLog(data.result || "No result", customPrompt);

    } catch (err) {
        console.error("Analysis error:", err);
        addLog("Error: " + err.message);
    }

    // Schedule next iteration immediately if still running
    if (isRunning) {
        requestAnimationFrame(analyzeLoop);
    }
}

function addLog(text, promptText = "") {
    const item = document.createElement('div');
    item.className = 'log-item';
    
    const time = new Date().toLocaleTimeString();
    
    let content = `<div class="log-timestamp">${time}</div>`;
    content += `<div class="log-result">${text}</div>`;
    
    item.innerHTML = content;
    
    logContainer.prepend(item);
}
