const API_URL = window.location.protocol === "file:"
    ? "http://127.0.0.1:8000"
    : window.location.origin;

const imageInput = document.getElementById("imageInput");
const browseButton = document.getElementById("browseButton");
const uploadArea = document.getElementById("uploadArea");
const imagePreview = document.getElementById("imagePreview");
const previewContainer = document.getElementById("previewContainer");
const fileName = document.getElementById("fileName");
const analyzeButton = document.getElementById("analyzeButton");
const removeImageButton = document.getElementById("removeImage");
const inspectionMode = document.getElementById("inspectionMode");
const datasetGroup = document.getElementById("datasetGroup");
const message = document.getElementById("message");
const downloadReportButton = document.getElementById("downloadReportButton");

let selectedFile = null;
let previewURL = null;
let chartInstance = null;
let latestInspection = null;
let totalInspections = 0;
let totalDefects = 0;

let historyRecords = JSON.parse(
    localStorage.getItem("fabricInspectionHistory") || "[]"
);

renderHistory();

// Check backend connection
async function checkBackend() {
    const status = document.getElementById("connectionStatus");

    try {
        const response = await fetch(`${API_URL}/health`);

        if (!response.ok) throw new Error("Backend unavailable");

        status.textContent = "Connected";
        status.style.color = "#16a36a";
    } catch (error) {
        status.textContent = "Disconnected";
        status.style.color = "#ef4444";
    }
}

checkBackend();

// Inspection mode selection
inspectionMode.addEventListener("change", () => {
    datasetGroup.hidden = inspectionMode.value !== "predict";
});

// Browse image
browseButton.addEventListener("click", () => {
    imageInput.click();
});

imageInput.addEventListener("change", () => {
    if (imageInput.files.length > 0) {
        handleImage(imageInput.files[0]);
    }
});

// Drag and drop
uploadArea.addEventListener("dragover", (event) => {
    event.preventDefault();
    uploadArea.classList.add("dragover");
});

uploadArea.addEventListener("dragleave", () => {
    uploadArea.classList.remove("dragover");
});

uploadArea.addEventListener("drop", (event) => {
    event.preventDefault();
    uploadArea.classList.remove("dragover");

    const file = event.dataTransfer.files[0];

    if (file) handleImage(file);
});

// Handle selected image
function handleImage(file) {
    if (!["image/jpeg", "image/png"].includes(file.type)) {
        showMessage("Please select a JPG or PNG image.", true);
        return;
    }

    selectedFile = file;

    if (previewURL) URL.revokeObjectURL(previewURL);

    previewURL = URL.createObjectURL(file);

    imagePreview.src = previewURL;
    fileName.textContent = file.name;

    previewContainer.hidden = false;
    analyzeButton.disabled = false;

    showMessage("Image selected successfully.");
}

// Remove selected image
removeImageButton.addEventListener("click", () => {
    selectedFile = null;

    if (previewURL) URL.revokeObjectURL(previewURL);

    previewURL = null;
    imageInput.value = "";
    imagePreview.src = "";

    previewContainer.hidden = true;
    analyzeButton.disabled = true;

    showMessage("Image removed.");
});

// Display messages
function showMessage(text, isError = false) {
    message.textContent = text;
    message.style.color = isError ? "#dc2626" : "#64748b";
}

// Analyse image
analyzeButton.addEventListener("click", async () => {
    if (!selectedFile) {
        showMessage("Please select an image first.", true);
        return;
    }

    const mode = inspectionMode.value;

    const formData = new FormData();
    formData.append("image", selectedFile);

    let endpoint = "/detect";

    if (mode === "predict") {
        endpoint = "/predict";
        formData.append(
            "dataset_name",
            document.getElementById("datasetName").value
        );
    }

    analyzeButton.disabled = true;
    analyzeButton.textContent = "Analysing...";
    showMessage("AI model is analysing your fabric image...");

    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Analysis failed");
        }

        if (mode === "detect") {
            displayDetectionResults(result);
        } else {
            displayClassificationResults(result);
        }

        updateStatistics(result, mode);
        addHistory(result, mode);

        latestInspection = {
            result,
            mode,
            file: selectedFile,
            inspectedAt: new Date()
        };

        if (downloadReportButton) {
            downloadReportButton.disabled = false;
        }

        document.getElementById("resultsSection").hidden = false;

        document.getElementById("resultsSection").scrollIntoView({
            behavior: "smooth"
        });

        showMessage("Analysis completed successfully.");

    } catch (error) {
        console.error(error);
        showMessage(error.message || "Unable to connect to backend.", true);

    } finally {
        analyzeButton.disabled = false;
        analyzeButton.textContent = "Analyse Fabric";
    }
});

// Draw detection boxes on the uploaded image
function drawDetectionImage(detections) {
    const container = document.querySelector(".result-image-container");
    container.innerHTML = "";

    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");

    const image = new Image();

    image.onload = () => {
        canvas.width = image.naturalWidth;
        canvas.height = image.naturalHeight;

        context.drawImage(image, 0, 0);

        detections.forEach((item) => {
            const [x1, y1, x2, y2] = item.box;

            context.strokeStyle = "#ef4444";
            context.lineWidth = Math.max(2, canvas.width / 250);
            context.strokeRect(x1, y1, x2 - x1, y2 - y1);

            const label = `${item.class_name} ${item.confidence}%`;

            context.font = `${Math.max(12, canvas.width / 35)}px Arial`;

            const labelWidth = context.measureText(label).width + 10;
            const labelHeight = Math.max(20, canvas.width / 30);

            context.fillStyle = "#ef4444";
            context.fillRect(
                x1,
                Math.max(0, y1 - labelHeight),
                labelWidth,
                labelHeight
            );

            context.fillStyle = "#ffffff";
            context.fillText(
                label,
                x1 + 5,
                Math.max(labelHeight - 5, y1 - 5)
            );
        });

        canvas.style.maxWidth = "100%";
        canvas.style.maxHeight = "420px";
        canvas.style.height = "auto";

        container.appendChild(canvas);
    };

    image.src = previewURL;
}

// YOLO detection results
function displayDetectionResults(result) {
    const detections = result.detections || [];

    drawDetectionImage(detections);

    document.getElementById("resultSummary").innerHTML = `
        <div class="result-item">
            <strong>Total Defects</strong>
            <span>${result.total_defects}</span>
        </div>
    `;

    const list = document.getElementById("detectionList");

    if (detections.length === 0) {
        list.innerHTML = `
            <div class="result-item">
                <strong>No defects detected</strong>
                <span>No objects passed the current confidence threshold.</span>
            </div>
        `;
    } else {
        list.innerHTML = detections.map((item, index) => `
            <div class="result-item">
                <strong>Defect ${index + 1}: ${escapeHTML(item.class_name)}</strong>
                <span>Confidence: ${Number(item.confidence).toFixed(2)}%</span>
                <br>
                <span>Bounding box: ${item.box.map(v => Number(v).toFixed(1)).join(", ")}</span>
            </div>
        `).join("");
    }

    updateChart(
        detections.map(item => item.class_name),
        detections.map(item => Number(item.confidence))
    );
}

// MobileNetV2 classification results
function displayClassificationResults(result) {
    const container = document.querySelector(".result-image-container");

    container.innerHTML = "";

    const image = document.createElement("img");
    image.src = previewURL;
    image.alt = "Classified fabric image";

    container.appendChild(image);

    const predictedClass =
        result.predicted_class ||
        result.class_name ||
        result.prediction ||
        "Unknown";

    const confidence = Number(result.confidence || 0);

    document.getElementById("resultSummary").innerHTML = `
        <div class="result-item">
            <strong>Predicted Class</strong>
            <span>${escapeHTML(predictedClass)}</span>
        </div>
        <div class="result-item">
            <strong>Confidence</strong>
            <span>${confidence.toFixed(2)}%</span>
        </div>
    `;

    document.getElementById("detectionList").innerHTML = `
        <div class="result-item">
            <strong>Classification Result</strong>
            <span>Whole-image classification. No bounding boxes are generated.</span>
        </div>
    `;

    const probabilities = result.probabilities || {};

    const labels = Object.keys(probabilities);
    const values = Object.values(probabilities).map(Number);

    updateChart(labels, values);
}

// Confidence chart
function updateChart(labels, values) {
    // A chart is optional; a CDN outage must not block the inspection results
    // or the PDF report button from being shown.
    if (typeof Chart === "undefined") {
        console.warn("Chart.js is unavailable; skipping confidence chart.");
        return;
    }

    const canvas = document.getElementById("confidenceChart");

    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(canvas, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Confidence (%)",
                data: values,
                backgroundColor: "#6259e8",
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: "Confidence (%)"
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Update dashboard statistics
function updateStatistics(result, mode) {
    totalInspections++;

    let defectCount = 0;
    let confidence = 0;

    if (mode === "detect") {
        defectCount = result.total_defects || 0;

        if (result.detections?.length) {
            confidence = Math.max(
                ...result.detections.map(item => Number(item.confidence))
            );
        }
    } else {
        confidence = Number(result.confidence || 0);
    }

    totalDefects += defectCount;

    document.getElementById("totalInspections").textContent =
        totalInspections;

    document.getElementById("totalDefects").textContent =
        totalDefects;

    document.getElementById("latestConfidence").textContent =
        mode === "detect" && defectCount === 0
            ? "--"
            : `${confidence.toFixed(2)}%`;
}

// Inspection history
function renderHistory() {
    const body = document.getElementById("historyBody");

    if (historyRecords.length === 0) {
        body.innerHTML = `
            <tr>
                <td colspan="5">No inspections performed yet.</td>
            </tr>
        `;
        return;
    }

    body.innerHTML = historyRecords.map(item => `
        <tr>
            <td>${escapeHTML(item.image)}</td>
            <td>${escapeHTML(item.mode)}</td>
            <td>${escapeHTML(item.result)}</td>
            <td>${Number(item.confidence).toFixed(2)}%</td>
            <td>${escapeHTML(item.time)}</td>
        </tr>
    `).join("");
}

function addHistory(result, mode) {
    let resultName = "";
    let confidence = 0;

    if (mode === "detect") {
        resultName = result.detections?.length
            ? result.detections.map(item => item.class_name).join(", ")
            : "No defects detected";

        if (result.detections?.length) {
            confidence = Math.max(
                ...result.detections.map(item => Number(item.confidence))
            );
        }
    } else {
        resultName =
            result.predicted_class ||
            result.class_name ||
            result.prediction ||
            "Unknown";

        confidence = Number(result.confidence || 0);
    }

    const record = {
        image: selectedFile.name,
        mode: mode === "detect" ? "YOLOv8" : "MobileNetV2",
        result: resultName,
        confidence: confidence,
        time: new Date().toLocaleString()
    };

    historyRecords.unshift(record);

    historyRecords = historyRecords.slice(0, 100);

    localStorage.setItem(
        "fabricInspectionHistory",
        JSON.stringify(historyRecords)
    );

    renderHistory();
}

// PDF report generation
if (downloadReportButton) {
    downloadReportButton.addEventListener(
        "click",
        downloadInspectionReport
    );
}

async function fileToDataURL(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(
            new Error("Could not read the inspected image.")
        );

        reader.readAsDataURL(file);
    });
}

async function downloadInspectionReport() {
    if (!latestInspection) {
        showMessage("Analyse an image before downloading a report.", true);
        return;
    }

    if (!window.jspdf || !window.jspdf.jsPDF) {
        showMessage(
            "PDF library not loaded. Check the jsPDF script in index.html.",
            true
        );
        return;
    }

    downloadReportButton.disabled = true;

    const originalLabel = downloadReportButton.textContent;
    downloadReportButton.textContent = "Generating PDF...";

    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({
            unit: "mm",
            format: "a4"
        });

        const result = latestInspection.result;
        const isDetection = latestInspection.mode === "detect";

        const pageWidth = doc.internal.pageSize.getWidth();
        const margin = 15;
        const usableWidth = pageWidth - margin * 2;

        let y = 20;

        doc.setFont("helvetica", "bold");
        doc.setFontSize(19);
        doc.text("Fabric Defect Inspection Report", margin, y);

        y += 7;

        doc.setFont("helvetica", "normal");
        doc.setFontSize(9);
        const projectTitle = doc.splitTextToSize(
            "Hybrid Deep Learning Frameworks for Fabric Defect Detection in Smart Garment Manufacturing",
            usableWidth
        );
        doc.text(projectTitle, margin, y);
        y += projectTitle.length * 4 + 3;

        doc.setFont("helvetica", "normal");
        doc.setFontSize(10);
        doc.text(
            `Generated: ${latestInspection.inspectedAt.toLocaleString()}`,
            margin,
            y
        );

        y += 8;

        doc.setDrawColor(210);
        doc.line(margin, y, pageWidth - margin, y);

        y += 9;

        const addField = (label, value) => {
            doc.setFont("helvetica", "bold");
            doc.setFontSize(11);
            doc.text(`${label}:`, margin, y);

            doc.setFont("helvetica", "normal");

            const lines = doc.splitTextToSize(
                String(value),
                usableWidth - 35
            );

            doc.text(lines, margin + 35, y);

            y += Math.max(7, lines.length * 5);
        };

        addField(
            "Image",
            latestInspection.file?.name || "Uploaded image"
        );

        addField(
            "Inspection method",
            isDetection
                ? "YOLOv8 Object Detection"
                : "MobileNetV2 Classification"
        );

        if (isDetection) {
            const detections = result.detections || [];

            addField(
                "Total defects detected",
                result.total_defects ?? detections.length
            );

            y += 2;

            doc.setFont("helvetica", "bold");
            doc.text("Detected defects", margin, y);

            y += 7;

            if (detections.length === 0) {
                doc.setFont("helvetica", "normal");
                doc.text(
                    "No objects passed the model confidence threshold.",
                    margin,
                    y
                );

                y += 7;
            } else {
                detections.forEach((item, index) => {
                    const line =
                        `${index + 1}. ${item.class_name} — ` +
                        `${Number(item.confidence).toFixed(2)}% confidence; ` +
                        `box [${(item.box || []).map(value => Number(value).toFixed(1)).join(", ")}]`;

                    const lines = doc.splitTextToSize(
                        line,
                        usableWidth
                    );

                    if (y + lines.length * 5 > 275) {
                        doc.addPage();
                        y = 20;
                    }

                    doc.setFont("helvetica", "normal");
                    doc.text(lines, margin, y);

                    y += Math.max(6, lines.length * 5);
                });
            }
        } else {
            const predictedClass =
                result.predicted_class ||
                result.class_name ||
                result.prediction ||
                "Unknown";

            addField("Predicted class", predictedClass);

            addField(
                "Confidence",
                `${Number(result.confidence || 0).toFixed(2)}%`
            );
        }

        // Include the annotated detection image when available.
        let imageData = null;
        let imageType = "JPEG";

        if (isDetection) {
            const annotatedCanvas = document.querySelector(
                ".result-image-container canvas"
            );

            if (annotatedCanvas) {
                imageData = annotatedCanvas.toDataURL("image/png");
                imageType = "PNG";
            }
        }

        if (!imageData && latestInspection.file) {
            imageData = await fileToDataURL(latestInspection.file);

            imageType =
                latestInspection.file.type === "image/png"
                    ? "PNG"
                    : "JPEG";
        }

        if (imageData) {
            const image = new Image();
            image.src = imageData;

            await new Promise((resolve, reject) => {
                image.onload = resolve;
                image.onerror = () => reject(
                    new Error("Could not prepare the image for the PDF.")
                );
            });

            const maxWidth = usableWidth;
            const maxHeight = 95;

            const scale = Math.min(
                maxWidth / image.width,
                maxHeight / image.height
            );

            const imageWidth = image.width * scale;
            const imageHeight = image.height * scale;

            if (y + imageHeight + 20 > 285) {
                doc.addPage();
                y = 20;
            }

            y += 5;

            doc.setFont("helvetica", "bold");
            doc.setFontSize(11);

            doc.text(
                isDetection
                    ? "Inspection image with detections"
                    : "Inspected image",
                margin,
                y
            );

            y += 5;

            doc.addImage(
                imageData,
                imageType,
                margin,
                y,
                imageWidth,
                imageHeight
            );

            y += imageHeight + 8;
        }

        if (y + 22 > 285) {
            doc.addPage();
            y = 20;
        }

        doc.setFont("helvetica", "italic");
        doc.setFontSize(8);

        const note =
            "Note: Confidence is the model's prediction confidence, " +
            "not overall model accuracy. Results should be verified " +
            "by a qualified inspector before production decisions.";

        doc.text(
            doc.splitTextToSize(note, usableWidth),
            margin,
            y
        );

        const safeName = (
            latestInspection.file?.name || "fabric_image"
        )
            .replace(/\.[^.]+$/, "")
            .replace(/[^a-z0-9_-]/gi, "_");

        doc.save(`Fabric_Inspection_Report_${safeName}.pdf`);

        showMessage("PDF inspection report downloaded.");

    } catch (error) {
        console.error(error);

        showMessage(
            error.message || "Could not generate the PDF report.",
            true
        );

    } finally {
        downloadReportButton.disabled = !latestInspection;
        downloadReportButton.textContent = originalLabel;
    }
}

// Escape text before displaying API values
function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}
