const apiStatus = document.getElementById("apiStatus");
const apiDot = document.getElementById("apiDot");
const apiText = document.getElementById("apiText");
const apiBaseInput = document.getElementById("apiBase");
const checkApiBtn = document.getElementById("checkApi");
const documentFileInput = document.getElementById("documentFile");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");
const ragQuery = document.getElementById("ragQuery");
const ragSummaryType = document.getElementById("ragSummaryType");
const ragLength = document.getElementById("ragLength");
const ragSummarizeBtn = document.getElementById("ragSummarizeBtn");
const ragStatus = document.getElementById("ragStatus");
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

let uploadedDocuments = [];

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

const setUploadStatus = (state, text) => {
  uploadStatus.dataset.state = state;
  uploadStatus.textContent = text;
};

const setRagStatus = (state, text) => {
  ragStatus.dataset.state = state;
  ragStatus.textContent = text;
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
  const files = Array.from(documentFileInput.files || []);
  if (files.length === 0) {
    setUploadStatus("error", "Choose one or more files before uploading.");
    return;
  }

  const baseUrl = normalizeBase(apiBaseInput.value || defaultBaseUrl);
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });

  uploadBtn.disabled = true;
  setUploadStatus(
    "pending",
    files.length === 1 ? `Uploading ${files[0].name}...` : `Uploading ${files.length} files...`,
  );

  try {
    const response = await fetch(`${baseUrl}/api/v1/documents/upload`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.detail || `Upload failed: ${response.status}`);
    }

    uploadedDocuments = Array.isArray(data.documents) ? data.documents : [];
    setUploadStatus("success", data.message || "Files uploaded successfully.");
    setRagStatus(
      uploadedDocuments.length > 0 ? "success" : "idle",
      uploadedDocuments.length > 0
        ? `Ready to summarize ${uploadedDocuments.length} uploaded document${uploadedDocuments.length === 1 ? "" : "s"}.`
        : "Upload documents first, then ask for a summary.",
    );
  } catch (error) {
    uploadedDocuments = [];
    setUploadStatus("error", error.message || "Unable to upload the selected file.");
    setRagStatus("error", "Upload failed, so there are no documents available for RAG summary.");
  } finally {
    uploadBtn.disabled = false;
  }
};

const summarizeUploadedDocuments = async () => {
  outputText.value = "";
  updateCharacterCount(outputCharacterCount, "");

  if (uploadedDocuments.length === 0) {
    setRagStatus("error", "Upload one or more documents before requesting a document-based summary.");
    return;
  }

  const query = ragQuery.value.trim();
  if (!query) {
    setRagStatus("error", "Enter a question or summary request for the uploaded documents.");
    return;
  }

  const baseUrl = normalizeBase(apiBaseInput.value || defaultBaseUrl);

  ragSummarizeBtn.disabled = true;
  ragSummarizeBtn.textContent = "Summarizing docs...";
  setRagStatus("pending", "Generating a summary from the uploaded documents. It will appear in the summary output box below once you scroll down.");

  try {
    const response = await fetch(`${baseUrl}/api/v1/summaries/rag`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query,
        top_k: 5,
        document_ids: uploadedDocuments.map((document) => document.id),
        summary_type: ragSummaryType.value,
        length: ragLength.value,
      }),
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.detail || `RAG summary failed: ${response.status}`);
    }

    const summary = data.summary || "";
    outputText.value = summary;
    updateCharacterCount(outputCharacterCount, summary);
    setRagStatus(
      "success",
      data.sources?.length
        ? `Summary generated using ${data.sources.length} matching source chunk${data.sources.length === 1 ? "" : "s"}. Scroll down to view it in the summary output box.`
        : "Summary generated. Scroll down to view it in the summary output box.",
    );
  } catch (error) {
    outputText.value = "";
    updateCharacterCount(outputCharacterCount, "");
    setRagStatus("error", error.message || "Unable to summarize the uploaded documents.");
  } finally {
    ragSummarizeBtn.disabled = false;
    ragSummarizeBtn.textContent = "Summarize uploaded docs";
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
  ragQuery.value = "";
  updateCharacterCount(inputCharacterCount, "");
  updateCharacterCount(outputCharacterCount, "");
});

checkApiBtn.addEventListener("click", checkApi);
uploadBtn.addEventListener("click", uploadDocument);
ragSummarizeBtn.addEventListener("click", summarizeUploadedDocuments);
documentFileInput.addEventListener("change", () => {
  const files = Array.from(documentFileInput.files || []);
  if (files.length === 0) {
    setUploadStatus("idle", "Choose one or more files to upload.");
    return;
  }

  if (files.length === 1) {
    setUploadStatus("idle", `Selected ${files[0].name}`);
    return;
  }

  setUploadStatus("idle", `Selected ${files.length} files`);
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
setRagStatus("idle", "Upload documents first, then ask for a summary.");
checkApi();
