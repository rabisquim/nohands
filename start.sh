#!/usr/bin/env bash
# Sobe o servidor Parakeet V3 local.
# Uso:  ./start.sh
set -euo pipefail

cd "$(dirname "$0")"

PY="${PYTHON:-python3}"

# 1) ffmpeg é obrigatório.
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "❌ ffmpeg não encontrado."
  echo "   Instale antes de continuar:"
  echo "     • Linux:  sudo apt install ffmpeg"
  echo "     • macOS:  brew install ffmpeg"
  exit 1
fi

# 2) Cria venv se não existir.
if [ ! -d ".venv" ]; then
  echo "📦 Criando ambiente virtual em .venv ..."
  "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

# 3) Instala/atualiza deps.
if [ ! -f ".venv/.deps_ok" ] || [ requirements.txt -nt .venv/.deps_ok ]; then
  echo "📥 Instalando dependências (1ª vez pode demorar) ..."
  pip install --upgrade pip >/dev/null
  pip install -r requirements.txt
  touch .venv/.deps_ok
fi

# 4) Sobe o servidor.
PORT="${PORT:-8765}"
HOST="${HOST:-127.0.0.1}"
echo
echo "🚀 Iniciando Parakeet V3 em http://${HOST}:${PORT}"
echo "   Abra o index.html pelo navegador (ex: cd . && python3 -m http.server 8080)"
echo "   A 1ª execução baixa o modelo (~600MB int8 ou ~1.2GB full). Seja paciente."
echo
HOST="$HOST" PORT="$PORT" python server.py
