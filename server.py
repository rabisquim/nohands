"""
Servidor local de transcrição de voz usando NVIDIA Parakeet TDT 0.6B v3.

Recebe áudio do navegador (webm/opus/wav/etc.), converte para wav 16kHz mono
via ffmpeg, transcreve com Parakeet V3 (onnx-asr) e devolve o texto em JSON.

Uso:
    python server.py
    # ou com GPU explícita:
    USE_GPU=1 python server.py
"""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import subprocess
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import onnx_asr
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# === CONFIGURAÇÃO ===
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8765"))
# Modelo padrão: v3 multilíngue. Troque para "nemo-parakeet-tdt-0.6b-v2"
# se quiser a v2 (inglês, levemente mais rápida) ou fixe em uma variante int8.
MODEL_NAME = os.environ.get("PARAKEET_MODEL", "nemo-parakeet-tdt-0.6b-v3")
QUANTIZATION: Optional[str] = os.environ.get("PARAKEET_QUANT", "int8")  # 'int8' | 'fp16' | None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("parakeet")

# Estado global do modelo (carregado no startup).
asr_model = None


def _detect_providers() -> list[str]:
    """Prefere CUDA se disponível, senão CPU. Pode ser forçado via env."""
    if os.environ.get("USE_GPU", "auto").lower() in ("0", "false", "no"):
        return ["CPUExecutionProvider"]
    try:
        import onnxruntime  # noqa: F401
        available = onnxruntime.get_available_providers()
        if "CUDAExecutionProvider" in available:
            log.info("🎮 GPU CUDA detectada — vou usar CUDAExecutionProvider.")
            return ["CUDAExecutionProvider", "CPUExecutionProvider"]
    except Exception as e:  # pragma: no cover
        log.warning("Não consegui checar providers ONNX: %s", e)
    log.info("💻 Sem GPU CUDA detectada — usando CPUExecutionProvider.")
    return ["CPUExecutionProvider"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carrega o Parakeet V3 uma única vez quando o servidor sobe."""
    global asr_model
    log.info("⏳ Carregando modelo %s (1ª vez baixa do HuggingFace, pode demorar)...", MODEL_NAME)
    providers = _detect_providers()
    try:
        kwargs = {"providers": providers}
        if QUANTIZATION:
            kwargs["quantization"] = QUANTIZATION
        asr_model = onnx_asr.load_model(MODEL_NAME, **kwargs)
    except Exception as e:
        log.exception("❌ Falha ao carregar o modelo")
        raise RuntimeError(f"Falha ao carregar {MODEL_NAME}: {e}") from e
    log.info("✅ Modelo pronto. Servidor escutando em http://%s:%d", HOST, PORT)
    yield
    log.info("👋 Encerrando servidor.")


app = FastAPI(title="Parakeet V3 Local ASR", version="1.0", lifespan=lifespan)

# CORS liberado p/ dev local (HTML aberto em outra porta).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _require_ffmpeg() -> None:
    if not shutil.which("ffmpeg"):
        raise HTTPException(
            status_code=500,
            detail=(
                "ffmpeg não encontrado no PATH. Instale:\n"
                "  • Linux:  sudo apt install ffmpeg\n"
                "  • macOS:  brew install ffmpeg\n"
                "  • Windows: https://www.gyan.dev/ffmpeg/builds/"
            ),
        )


def _convert_to_wav16k_mono(src: Path, dst: Path) -> None:
    """Converte qualquer formato de áudio (webm/opus/m4a/ogg/wav/...) para
    wav PCM 16kHz mono, que é o que o Parakeet espera."""
    proc = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel", "error",
            "-i", str(src),
            "-ar", "16000",   # 16 kHz
            "-ac", "1",       # mono
            "-sample_fmt", "s16",
            "-f", "wav",
            str(dst),
        ],
        capture_output=True,
    )
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", errors="ignore") or f"ffmpeg exit {proc.returncode}"
        raise HTTPException(status_code=400, detail=f"ffmpeg falhou: {err}")


@app.get("/health")
def health() -> dict:
    """Probe simples p/ o navegador saber se o backend está de pé."""
    return {
        "status": "ok" if asr_model is not None else "loading",
        "model": MODEL_NAME,
        "quantization": QUANTIZATION,
        "providers": _detect_providers(),
    }


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)) -> JSONResponse:
    if asr_model is None:
        raise HTTPException(status_code=503, detail="Modelo ainda carregando, tente em alguns segundos.")

    _require_ffmpeg()

    # 1) Salva o upload em arquivo temporário.
    suffix = Path(audio.filename or "audio").suffix or ".webm"
    tmp_in = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    try:
        content = await audio.read()
        if not content:
            raise HTTPException(status_code=400, detail="Arquivo de áudio vazio.")
        tmp_in.write(content)
        tmp_in.flush()
        tmp_in_path = Path(tmp_in.name)
    finally:
        tmp_in.close()

    tmp_out_path = tmp_in_path.with_suffix(".wav")
    try:
        # 2) Converte p/ wav 16k mono com ffmpeg.
        await asyncio.to_thread(_convert_to_wav16k_mono, tmp_in_path, tmp_out_path)

        # 3) Transcreve (bloqueia — roda em thread p/ não travar o event loop).
        text = await asyncio.to_thread(asr_model.recognize, str(tmp_out_path))
        if isinstance(text, list):  # onnx-asr pode retornar lista em chamadas em batch
            text = " ".join(str(t) for t in text)
        text = (text or "").strip()

        return JSONResponse({"text": text, "model": MODEL_NAME})
    finally:
        for p in (tmp_in_path, tmp_out_path):
            try:
                p.unlink()
            except OSError:
                pass


FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


def main() -> None:
    import uvicorn
    uvicorn.run(
        "server:app",
        host=HOST,
        port=PORT,
        log_level="info",
        reload=False,
    )


if __name__ == "__main__":
    main()
