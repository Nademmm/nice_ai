const api = {
  upload: "/api/upload",
  documents: "/api/documents"
};

const state = {
  files: []
};

const fileInput = document.getElementById("file-input");
const dropzone = document.getElementById("dropzone");
const selectedFiles = document.getElementById("selected-files");
const uploadBtn = document.getElementById("upload-btn");
const clearBtn = document.getElementById("clear-btn");
const uploadMessage = document.getElementById("upload-message");
const docsList = document.getElementById("docs-list");
const refreshBtn = document.getElementById("refresh-btn");
const docCount = document.getElementById("doc-count");

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function setMessage(text, type = "") {
  uploadMessage.textContent = text;
  uploadMessage.className = "upload-message";
  if (type) {
    uploadMessage.classList.add(type);
  }
}

function renderSelectedFiles() {
  selectedFiles.innerHTML = "";
  state.files.forEach((file) => {
    const li = document.createElement("li");
    li.className = "file-chip";
    const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
    li.textContent = `${file.name} (${sizeMb} MB)`;
    selectedFiles.appendChild(li);
  });

  const hasFiles = state.files.length > 0;
  uploadBtn.disabled = !hasFiles;
  clearBtn.disabled = !hasFiles;
}

function validateFiles(files) {
  const pdfFiles = [];
  for (const file of files) {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      continue;
    }
    if (file.size > 10 * 1024 * 1024) {
      setMessage(`File ${file.name} melebihi 10 MB.`, "error");
      continue;
    }
    pdfFiles.push(file);
  }

  if (pdfFiles.length > 10) {
    setMessage("Maksimal 10 file per upload.", "error");
    return [];
  }

  return pdfFiles;
}

function setFiles(files) {
  state.files = validateFiles(files);
  renderSelectedFiles();
  if (state.files.length > 0) {
    setMessage(`${state.files.length} file siap di-upload.`);
  }
}

fileInput.addEventListener("change", (event) => {
  setFiles(Array.from(event.target.files || []));
});

clearBtn.addEventListener("click", () => {
  state.files = [];
  fileInput.value = "";
  renderSelectedFiles();
  setMessage("Pilihan file dibersihkan.");
});

dropzone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", () => {
  dropzone.classList.remove("dragover");
});

dropzone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropzone.classList.remove("dragover");
  const files = Array.from(event.dataTransfer?.files || []);
  setFiles(files);
});

uploadBtn.addEventListener("click", async () => {
  if (!state.files.length) {
    return;
  }

  const formData = new FormData();
  state.files.forEach((file) => {
    formData.append("files", file);
  });

  uploadBtn.disabled = true;
  setMessage("Mengunggah dan mengindeks dokumen... mohon tunggu.");

  try {
    const response = await fetch(api.upload, {
      method: "POST",
      body: formData
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Upload gagal.");
    }

    setMessage(payload.message || "Upload berhasil.", "success");
    state.files = [];
    fileInput.value = "";
    renderSelectedFiles();
    await loadDocuments();
  } catch (error) {
    setMessage(error.message || "Terjadi kesalahan saat upload.", "error");
  } finally {
    uploadBtn.disabled = state.files.length === 0;
  }
});

function renderDocuments(items) {
  docsList.innerHTML = "";
  docCount.textContent = String(items.length);

  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "Belum ada dokumen yang diindeks.";
    docsList.appendChild(empty);
    return;
  }

  items.forEach((doc) => {
    const card = document.createElement("article");
    card.className = "doc-card";

    const source = doc.metadata?.source || "unknown";
    const type = doc.metadata?.type || "unknown";
    const safeSource = escapeHtml(source);
    const safeType = escapeHtml(type);
    const safeId = escapeHtml(doc.id || "");
    const safePreview = escapeHtml(doc.content_preview || "-");

    card.innerHTML = `
      <div class="doc-top">
        <div>
          <div class="doc-name">${safeSource}</div>
          <div class="doc-meta">ID: ${safeId} | type: ${safeType}</div>
        </div>
        <button class="doc-delete" data-id="${safeId}">Hapus</button>
      </div>
      <div class="doc-preview">${safePreview}</div>
    `;

    docsList.appendChild(card);
  });
}

async function loadDocuments() {
  try {
    const response = await fetch(api.documents);
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Gagal memuat dokumen.");
    }
    renderDocuments(payload.documents || []);
  } catch (error) {
    docsList.innerHTML = `<p class="empty-state">${error.message}</p>`;
  }
}

docsList.addEventListener("click", async (event) => {
  const button = event.target.closest(".doc-delete");
  if (!button) {
    return;
  }

  const documentId = button.dataset.id;
  if (!documentId) {
    return;
  }

  button.disabled = true;
  try {
    const response = await fetch(`/api/documents/${documentId}`, {
      method: "DELETE"
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Gagal menghapus dokumen.");
    }
    setMessage(payload.message || "Dokumen dihapus.", "success");
    await loadDocuments();
  } catch (error) {
    setMessage(error.message, "error");
  } finally {
    button.disabled = false;
  }
});

refreshBtn.addEventListener("click", loadDocuments);

loadDocuments();
