const socket = io();
const container = document.getElementById('pdf-viewer');

let pdfDoc = null;
let scale = 1.2;
let canvasMap = {};

// Scroll container to wrap viewer
document.body.style.height = '100vh';
document.body.style.overflow = 'auto';

// ---------- Load PDF ----------
pdfjsLib.getDocument('/pdf').promise.then(pdfDoc_ => {
  pdfDoc = pdfDoc_;
  for (let i = 1; i <= pdfDoc.numPages; i++) {
    renderPage(i);
  }
});

function renderPage(num) {
  pdfDoc.getPage(num).then(page => {
    const canvas = document.createElement('canvas');
    canvas.dataset.pageNum = num;
    const context = canvas.getContext('2d');
    const viewport = page.getViewport({ scale: scale });

    canvas.height = viewport.height;
    canvas.width = viewport.width;
    container.appendChild(canvas);

    canvasMap[num] = canvas;
    const renderContext = { canvasContext: context, viewport: viewport };
    return page.render(renderContext).promise;
  });
}

// ---------- Sync Scroll ----------
if (ROLE === "admin") {
  window.addEventListener("scroll", () => {
    socket.emit("scroll", { scrollTop: window.scrollY });
  });
} else {
  socket.on("scroll", data => {
    window.scrollTo({ top: data.scrollTop, behavior: "smooth" });
  });
}

// ---------- Highlight Toggle ----------
container.addEventListener("click", (e) => {
  if (ROLE !== "admin") return;

  const existing = e.target.classList.contains("highlight");
  if (existing) {
    e.target.remove();
    socket.emit("highlight", { remove: true, id: e.target.dataset.id });
    return;
  }

  const rect = container.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  const id = "hl_" + Date.now();

  const box = document.createElement("div");
  box.className = "highlight";
  box.dataset.id = id;
  box.style.top = y + 'px';
  box.style.left = x + 'px';
  box.style.width = '60px';
  box.style.height = '25px';
  box.style.position = 'absolute';
  box.style.zIndex = 10;
  container.appendChild(box);

  socket.emit("highlight", { x, y, id });
});

socket.on("highlight", data => {
  if (data.remove) {
    const el = document.querySelector(`[data-id="${data.id}"]`);
    if (el) el.remove();
    return;
  }

  const box = document.createElement("div");
  box.className = "highlight";
  box.dataset.id = data.id;
  box.style.top = data.y + 'px';
  box.style.left = data.x + 'px';
  box.style.width = '60px';
  box.style.height = '25px';
  box.style.position = 'absolute';
  box.style.zIndex = 10;
  container.appendChild(box);
});
