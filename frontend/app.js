const apiStatus = document.getElementById("apiStatus");
const apiDot = document.getElementById("apiDot");
const apiText = document.getElementById("apiText");
const apiBaseInput = document.getElementById("apiBase");
const checkApiBtn = document.getElementById("checkApi");
const summarizeBtn = document.getElementById("summarizeBtn");
const clearBtn = document.getElementById("clearBtn");
const inputText = document.getElementById("inputText");
const outputText = document.getElementById("outputText");
const summaryType = document.getElementById("summaryType");
const summaryLength = document.getElementById("summaryLength");
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

const summarizeMock = (text) => {
  if (!text.trim()) {
    return "";
  }
  const sentences = text.split(/(?<=[.!?])\s+/).slice(0, 3);
  const preview = sentences.join(" ").trim();
  if (summaryType.value === "bullet") {
    return sentences.map((line) => `• ${line.trim()}`).join("\n");
  }
  return preview;
};

const summarizeWithApi = async () => {
  const baseUrl = normalizeBase(apiBaseInput.value || defaultBaseUrl);
  const payload = {
    text: inputText.value,
    summary_type: summaryType.value,
    length: summaryLength.value,
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
  return data.summary || data.result || "";
};

summarizeBtn.addEventListener("click", async () => {
  outputText.value = "";
  const content = inputText.value.trim();
  if (!content) {
    outputText.value = "Please paste some content to summarize.";
    return;
  }

  summarizeBtn.disabled = true;
  summarizeBtn.textContent = "Summarizing...";

  try {
    if (mockMode.checked) {
      outputText.value = summarizeMock(content);
    } else {
      outputText.value = await summarizeWithApi();
    }
  } catch (error) {
    outputText.value = "Unable to summarize via API. Enable mock mode or check the API URL.";
  } finally {
    summarizeBtn.disabled = false;
    summarizeBtn.textContent = "Summarize";
  }
});

clearBtn.addEventListener("click", () => {
  inputText.value = "";
  outputText.value = "";
});

checkApiBtn.addEventListener("click", checkApi);

checkApi();
