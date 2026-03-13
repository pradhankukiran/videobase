const $ = (sel) => document.querySelector(sel);

// State
let currentVideoId = null;

// Elements
const dropZone = $("#drop-zone");
const videoInput = $("#video-input");
const transcriptInput = $("#transcript-input");
const uploadBtn = $("#upload-btn");
const uploadProgress = $("#upload-progress");
const progressFill = $("#progress-fill");
const progressText = $("#progress-text");
const uploadError = $("#upload-error");
const uploadSection = $("#upload-section");
const playerSection = $("#player-section");
const videoPlayer = $("#video-player");
const videoTitle = $("#video-title");
const searchInput = $("#search-input");
const searchResults = $("#search-results");
const searchStatus = $("#search-status");
const newVideoBtn = $("#new-video-btn");

// Drag and drop
dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});
dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  const files = e.dataTransfer.files;
  for (const file of files) {
    if (file.type.startsWith("video/") || /\.(mkv|mp4|webm|ogg)$/i.test(file.name)) {
      videoInput.files = createFileList(file);
      updateFileLabel("video-label", file.name);
    } else if (/\.(srt|vtt|sbv)$/i.test(file.name)) {
      transcriptInput.files = createFileList(file);
      updateFileLabel("transcript-label", file.name);
    }
  }
});

function createFileList(file) {
  const dt = new DataTransfer();
  dt.items.add(file);
  return dt.files;
}

function updateFileLabel(id, name) {
  const el = document.getElementById(id);
  if (el) el.textContent = name;
}

videoInput.addEventListener("change", () => {
  if (videoInput.files[0]) updateFileLabel("video-label", videoInput.files[0].name);
});
transcriptInput.addEventListener("change", () => {
  if (transcriptInput.files[0]) updateFileLabel("transcript-label", transcriptInput.files[0].name);
});

// Upload
uploadBtn.addEventListener("click", () => {
  if (!videoInput.files[0]) {
    showError("Please select a video file.");
    return;
  }
  uploadVideo(videoInput.files[0], transcriptInput.files[0] || null);
});

function uploadVideo(videoFile, transcriptFile) {
  const form = new FormData();
  form.append("video", videoFile);
  if (transcriptFile) form.append("transcript", transcriptFile);

  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/api/upload");

  // Show progress
  uploadProgress.classList.remove("hidden");
  uploadError.classList.add("hidden");
  uploadBtn.disabled = true;
  uploadBtn.textContent = "Uploading...";

  xhr.upload.addEventListener("progress", (e) => {
    if (e.lengthComputable) {
      const pct = Math.round((e.loaded / e.total) * 100);
      progressFill.style.width = pct + "%";
      progressText.textContent = pct < 100 ? `Uploading... ${pct}%` : "Indexing transcript...";
    }
  });

  xhr.addEventListener("load", () => {
    uploadBtn.disabled = false;
    uploadBtn.textContent = "Upload & Index";
    if (xhr.status === 200) {
      const data = JSON.parse(xhr.responseText);
      currentVideoId = data.video_id;
      showPlayer(data);
    } else {
      let msg = "Upload failed.";
      try {
        msg = JSON.parse(xhr.responseText).detail;
      } catch {}
      showError(msg);
      uploadProgress.classList.add("hidden");
    }
  });

  xhr.addEventListener("error", () => {
    uploadBtn.disabled = false;
    uploadBtn.textContent = "Upload & Index";
    showError("Network error — is the server running?");
    uploadProgress.classList.add("hidden");
  });

  xhr.send(form);
}

function showError(msg) {
  uploadError.textContent = msg;
  uploadError.classList.remove("hidden");
}

function showPlayer(data) {
  uploadSection.classList.add("hidden");
  playerSection.classList.remove("hidden");
  videoPlayer.src = `/api/video/${data.video_id}`;
  videoTitle.textContent = data.filename;
  $("#segment-count").textContent = `${data.segment_count} searchable chunks indexed`;
  searchInput.focus();
}

// New video
newVideoBtn.addEventListener("click", () => {
  playerSection.classList.add("hidden");
  uploadSection.classList.remove("hidden");
  uploadProgress.classList.add("hidden");
  uploadError.classList.add("hidden");
  videoInput.value = "";
  transcriptInput.value = "";
  updateFileLabel("video-label", "Choose video file");
  updateFileLabel("transcript-label", "Choose transcript (optional)");
  searchInput.value = "";
  searchResults.innerHTML = "";
  searchStatus.textContent = "";
  currentVideoId = null;
});

// Search with debounce
let searchTimeout = null;
searchInput.addEventListener("input", () => {
  clearTimeout(searchTimeout);
  const q = searchInput.value.trim();
  if (!q) {
    searchResults.innerHTML = "";
    searchStatus.textContent = "";
    return;
  }
  searchStatus.textContent = "Searching...";
  searchTimeout = setTimeout(() => doSearch(q), 300);
});

async function doSearch(query) {
  if (!currentVideoId) return;
  try {
    const res = await fetch(
      `/api/search?video_id=${encodeURIComponent(currentVideoId)}&q=${encodeURIComponent(query)}`
    );
    if (!res.ok) {
      searchStatus.textContent = "Search failed.";
      return;
    }
    const results = await res.json();
    renderResults(results);
  } catch {
    searchStatus.textContent = "Search error.";
  }
}

function renderResults(results) {
  if (results.length === 0) {
    searchResults.innerHTML = "";
    searchStatus.textContent = "No results found.";
    return;
  }
  searchStatus.textContent = `${results.length} result${results.length > 1 ? "s" : ""}`;
  searchResults.innerHTML = results
    .map(
      (r, i) => `
    <div class="result-card flex items-start gap-3 p-3 rounded-lg border border-slate-200 cursor-pointer fade-in"
         style="animation-delay: ${i * 40}ms"
         onclick="jumpTo(${r.start_time})">
      <span class="timestamp shrink-0 inline-flex items-center px-2 py-1 rounded bg-indigo-100 text-indigo-700 text-sm font-medium">
        ${formatTime(r.start_time)}
      </span>
      <div class="flex-1 min-w-0">
        <p class="text-sm text-slate-700 leading-relaxed">${escapeHtml(r.text)}</p>
        <div class="mt-1.5 flex items-center gap-2">
          <div class="h-1.5 flex-1 max-w-[100px] bg-slate-100 rounded-full overflow-hidden">
            <div class="score-bar h-full bg-indigo-400 rounded-full" style="width: ${Math.round(r.score * 100)}%"></div>
          </div>
          <span class="text-xs text-slate-400">${Math.round(r.score * 100)}%</span>
        </div>
      </div>
    </div>
  `
    )
    .join("");
}

function jumpTo(seconds) {
  videoPlayer.currentTime = seconds;
  videoPlayer.play();
  videoPlayer.scrollIntoView({ behavior: "smooth", block: "center" });
}

function formatTime(secs) {
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  const s = Math.floor(secs % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${m}:${String(s).padStart(2, "0")}`;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// Expose jumpTo globally for onclick
window.jumpTo = jumpTo;
