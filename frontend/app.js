const apiStatus = document.getElementById("apiStatus");
const apiDot = document.getElementById("apiDot");
const apiText = document.getElementById("apiText");
const apiBaseInput = document.getElementById("apiBase");
const checkApiBtn = document.getElementById("checkApi");
const documentFileInput = document.getElementById("documentFile");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");
const uploadedDocumentPanel = document.getElementById("uploadedDocumentPanel");
const uploadedDocumentBadge = document.getElementById("uploadedDocumentBadge");
const uploadedOriginalFilename = document.getElementById("uploadedOriginalFilename");
const uploadedStoredFilename = document.getElementById("uploadedStoredFilename");
const uploadedContentType = document.getElementById("uploadedContentType");
const uploadedFileSize = document.getElementById("uploadedFileSize");
const uploadedProcessingStatus = document.getElementById("uploadedProcessingStatus");
const uploadedCreatedAt = document.getElementById("uploadedCreatedAt");
const summarizeBtn = document.getElementById("summarizeBtn");
const clearBtn = document.getElementById("clearBtn");
const inputText = document.getElementById("inputText");
const outputText = document.getElementById("outputText");
const inputCharacterCount = document.getElementById("inputCharacterCount");
const outputCharacterCount = document.getElementById("outputCharacterCount");
const summaryType = document.getElementById("summaryType");
const summaryLength = document.getElementById("summaryLength");
const customLengthField = document.getElementById("customLengthField");
const customLengthInput = document.getElementById("customLength");
const mockMode = document.getElementById("mockMode");

const isFileOrigin = window.location.protocol === "file:";
const defaultBaseUrl = window.location.port === "5173" || isFileOrigin
  ? "http://localhost:8000"
  : window.location.origin;
apiBaseInput.value = defaultBaseUrl;

const setStatus = (state, text) => {
  apiText.textContent = text;
  apiDot.style.background = state === "ok" ? "#22c55e" : state === "error" ? "#ef4444" : "#94a3b8";
  apiStatus.title = text;
};

const normalizeBase = (value) => value.replace(/\/$/, "");

const formatBytes = (value) => {
  if (!Number.isFinite(value) || value < 0) {
    return "-";
  }

  if (value < 1024) {
    return `${value} B`;
  }

  const units = ["KB", "MB", "GB"];
  let size = value / 1024;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }

  return `${size.toFixed(size >= 10 ? 0 : 1)} ${units[unitIndex]}`;
};

const formatTimestamp = (value) => {
  if (!value) {
    return "-";
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleString();
};

const setUploadStatus = (state, text) => {
  uploadStatus.dataset.state = state;
  uploadStatus.textContent = text;
};

const renderUploadedDocument = (document) => {
  uploadedDocumentPanel.hidden = false;
  uploadedDocumentBadge.textContent = document.status || "Uploaded";
  uploadedOriginalFilename.textContent = document.original_filename || "-";
  uploadedStoredFilename.textContent = document.stored_filename || "-";
  uploadedContentType.textContent = document.content_type || "Unknown";
  uploadedFileSize.textContent = formatBytes(document.file_size_bytes);
  uploadedProcessingStatus.textContent = document.status || "-";
  uploadedCreatedAt.textContent = formatTimestamp(document.created_at);
};

const countCharacters = (text) => text.length;

const updateCharacterCount = (element, text) => {
  element.textContent = String(countCharacters(text));
};

const getInputLength = () => countCharacters(inputText.value);

const getCustomLength = () => {
  if (summaryLength.value !== "custom") {
    return null;
  }

  const parsed = Number.parseInt(customLengthInput.value, 10);
  if (!Number.isFinite(parsed) || parsed < 1) {
    return null;
  }

  return parsed;
};

const getCustomLengthError = () => {
  if (summaryLength.value !== "custom") {
    return null;
  }

  const customLength = getCustomLength();
  if (!customLength) {
    return "Enter a custom character limit greater than 0.";
  }

  const inputLength = getInputLength();
  if (inputLength > 0 && customLength > inputLength) {
    return `Custom character limit cannot exceed the input length (${inputLength}).`;
  }

  return null;
};

const syncCustomLengthValidation = () => {
  const inputLength = getInputLength();
  customLengthInput.max = String(Math.max(inputLength, 1));

  const errorMessage = getCustomLengthError();
  customLengthInput.setCustomValidity(errorMessage || "");
  customLengthInput.title = inputLength > 0
    ? `Maximum allowed: ${inputLength} characters`
    : "Paste content before setting a custom character limit.";

  return errorMessage;
};

const updateCustomLengthVisibility = () => {
  const isCustom = summaryLength.value === "custom";

  customLengthField.hidden = !isCustom;
  customLengthInput.disabled = !isCustom;

  if (!isCustom) {
    customLengthInput.setCustomValidity("");
  }

  syncCustomLengthValidation();
};

const checkApi = async () => {
  const baseUrl = normalizeBase(apiBaseInput.value || defaultBaseUrl);
  setStatus("pending", "Checking API...");
  try {
    const response = await fetch(`${baseUrl}/api/v1/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    setStatus("ok", "API is healthy");
  } catch (error) {
    setStatus("error", "API unavailable");
  }
};

const uploadDocument = async () => {
  const [file] = documentFileInput.files;
  if (!file) {
    setUploadStatus("error", "Choose a file before uploading.");
    return;
  }

  const baseUrl = normalizeBase(apiBaseInput.value || defaultBaseUrl);
  const formData = new FormData();
  formData.append("file", file);

  uploadBtn.disabled = true;
  setUploadStatus("pending", `Uploading ${file.name}...`);

  try {
    const response = await fetch(`${baseUrl}/api/v1/documents/upload`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.detail || `Upload failed: ${response.status}`);
    }

    const uploadedDocument = data.document || {};
    renderUploadedDocument(uploadedDocument);
    setUploadStatus("success", data.message || data.messages || "File uploaded successfully.");
  } catch (error) {
    uploadedDocumentPanel.hidden = true;
    setUploadStatus("error", error.message || "Unable to upload the selected file.");
  } finally {
    uploadBtn.disabled = false;
  }
};

const summarizeMock = (text) => {
  if (!text.trim()) {
    return { summary: "" };
  }
  const sentences = text.split(/(?<=[.!?])\s+/).slice(0, 3);
  const preview = sentences.join(" ").trim();
  const customLength = getCustomLength();
  if (summaryType.value === "bullet") {
    const bulletPreview = sentences.map((line) => `• ${line.trim()}`).join("\n");
    const summary = customLength ? bulletPreview.slice(0, customLength).trim() : bulletPreview;
    return { summary };
  }
  const summary = customLength ? preview.slice(0, customLength).trim() : preview;
  return { summary };
};

const summarizeWithApi = async () => {
  const baseUrl = normalizeBase(apiBaseInput.value || defaultBaseUrl);

  const customLength = getCustomLength();

  const payload = {
    text: inputText.value,
    summary_type: summaryType.value,
    length: summaryLength.value === "custom" ? "custom" : summaryLength.value,
    max_length: summaryLength.value === "custom" ? customLength : null,
  };

  const response = await fetch(`${baseUrl}/api/v1/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Summarize failed: ${response.status}`);
  }

  const data = await response.json();
  return {
    summary: data.summary || data.summarized_text || data.result || "",
  };
};

summarizeBtn.addEventListener("click", async () => {
  outputText.value = "";
  updateCharacterCount(outputCharacterCount, "");
  const content = inputText.value.trim();
  if (!content) {
    outputText.value = "Please paste some content to summarize.";
    updateCharacterCount(outputCharacterCount, outputText.value);
    return;
  }

  const customLengthError = syncCustomLengthValidation();
  if (customLengthError) {
    outputText.value = customLengthError;
    updateCharacterCount(outputCharacterCount, outputText.value);
    customLengthInput.reportValidity();
    return;
  }

  summarizeBtn.disabled = true;
  summarizeBtn.textContent = "Summarizing...";

  try {
    let result;
    if (mockMode.checked) {
      result = summarizeMock(content);
    } else {
      result = await summarizeWithApi();
    }
    outputText.value = result.summary;
    updateCharacterCount(outputCharacterCount, result.summary);
  } catch (error) {
    outputText.value = "Unable to summarize via API. Enable mock mode or check the API URL.";
    updateCharacterCount(outputCharacterCount, outputText.value);
  } finally {
    summarizeBtn.disabled = false;
    summarizeBtn.textContent = "Summarize";
  }
});

clearBtn.addEventListener("click", () => {
  inputText.value = "";
  outputText.value = "";
  updateCharacterCount(inputCharacterCount, "");
  updateCharacterCount(outputCharacterCount, "");
});

checkApiBtn.addEventListener("click", checkApi);
uploadBtn.addEventListener("click", uploadDocument);
documentFileInput.addEventListener("change", () => {
  const [file] = documentFileInput.files;
  setUploadStatus("idle", file ? `Selected ${file.name}` : "Choose a file to upload.");
});
summaryLength.addEventListener("change", updateCustomLengthVisibility);
inputText.addEventListener("input", () => {
  updateCharacterCount(inputCharacterCount, inputText.value);
  syncCustomLengthValidation();
});
customLengthInput.addEventListener("input", syncCustomLengthValidation);

updateCustomLengthVisibility();
updateCharacterCount(inputCharacterCount, inputText.value);
updateCharacterCount(outputCharacterCount, outputText.value);
checkApi();
