# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path
import shutil
import pandas as pd
import os
from clasificacion import ejecutar_pipeline

app = FastAPI()

BASE = Path(__file__).resolve().parent
UPLOAD_DIR = BASE / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html no encontrado")
    return index_path.read_text(encoding="utf-8")


@app.get("/clasificacion", response_class=HTMLResponse)
async def serve_inicio():
    index_path = FRONTEND_DIR / "inicio.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="inicio.html no encontrado")
    return index_path.read_text(encoding="utf-8")


@app.get("/graficas", response_class=HTMLResponse)
async def serve_graficas():
    index_path = FRONTEND_DIR / "graficas.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="graficas.html no encontrado")
    return index_path.read_text(encoding="utf-8")


# --- Endpoint del pipeline ---
@app.post("/procesar/")
async def procesar(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .csv o .xlsx")

    destino = UPLOAD_DIR / file.filename
    with destino.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        resultado_path = ejecutar_pipeline(file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en pipeline: {e}")

    if not os.path.exists(resultado_path):
        raise HTTPException(status_code=500, detail=f"No se generó archivo de salida: {resultado_path}")

    return FileResponse(
        path=resultado_path,
        filename=os.path.basename(resultado_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
