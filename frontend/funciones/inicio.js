const sendBtn = document.getElementById("sendBtn");
const btnGraficas = document.getElementById("btnGraficas");
const fileInput = document.getElementById("fileInput");
const fileInfo = document.getElementById("fileInfo");

let selectedFile = null;
window.graficasRutas = null; // Variable global para almacenar las rutas

// Evento para seleccionar archivo
fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    selectedFile = fileInput.files[0];
    fileInfo.textContent = `Archivo seleccionado: ${selectedFile.name}`;
    sendBtn.disabled = false;
  } else {
    fileInfo.textContent = "";
    sendBtn.disabled = true;
  }
});

// Evento para enviar archivo
sendBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  sendBtn.disabled = true;
  sendBtn.textContent = "⏳ Procesando...";
  btnGraficas.disabled = true; // Desactivar botón gráficas mientras procesa

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    // Enviar archivo y descargar resultado
    const res = await fetch("http://127.0.0.1:8000/procesar/", {
      method: "POST",
      body: formData
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Error servidor: ${res.status} ${text}`);
    }

    const blob = await res.blob();

    // Nombre del archivo resultante
    const downloadName = selectedFile.name.replace(/\.[^/.]+$/, "") + "_resultado.csv";

    // Descargar automáticamente
    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = downloadName;
    document.body.appendChild(link);
    link.click();
    link.remove();

    sendBtn.textContent = "✅ Archivo descargado";  
  } catch (err) {
    console.error(err);
    alert("Error al procesar: " + err.message);
    sendBtn.textContent = "📤 Enviar archivo";
  } finally {
    sendBtn.disabled = false;
  }
});

document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("btnGraficas");
    btn.disabled = false;
    btn.addEventListener("click", () => {
        window.location.href = "/graficas";
    });
});

