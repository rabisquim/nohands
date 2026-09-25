# Plano de Implementação: Unificação da Execução (Servidor FastAPI + Frontend)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unificar o backend FastAPI e o frontend da aplicação em um único comando de execução (`./start.sh`), servindo os arquivos estáticos diretamente e abrindo o navegador automaticamente em sessões desktop.

**Architecture:** O FastAPI passará a montar o diretório estático `frontend/` na raiz (`/`) com `html=True` utilizando `StaticFiles`. O script `start.sh` cuidará da instalação do pacote `aiofiles` e disparará uma rotina não-bloqueante em background para abrir o navegador no endereço `http://${HOST}:${PORT}`. O arquivo `index.html` utilizará `window.location.origin` como padrão.

**Tech Stack:** Python 3.10+, FastAPI, Starlette `StaticFiles`, `aiofiles`, Uvicorn, Bash (`xdg-open`).

## Global Constraints

- O backend deve continuar expondo `/health` e `/transcribe` sem conflitos de rotas com arquivos estáticos.
- O script `start.sh` não deve falhar se o usuário estiver em ambiente headless (sem `$DISPLAY` ou sem `xdg-open`).
- Nenhum dado corporativo ou chaves externas devem ser referenciadas.
- Todas as mensagens e documentações em português.

---

### Task 1: Organização dos Arquivos e Atualização de Dependências

**Files:**
- Create: `frontend/index.html` (movido de `index.html`)
- Modify: `requirements.txt:1-13`
- Delete: `como rodar.txt`

**Interfaces:**
- Consumes: `index.html` existente.
- Produces: `frontend/index.html`, `requirements.txt` contendo `aiofiles>=23.2.0`.

- [ ] **Step 1: Mover `index.html` para `frontend/index.html` e remover `como rodar.txt`**

```bash
mkdir -p frontend
git mv index.html frontend/index.html
git rm "como rodar.txt"
```

- [ ] **Step 2: Adicionar `aiofiles` em `requirements.txt`**

Adicionar `aiofiles>=23.2.0` no arquivo `requirements.txt`:
```text
# Web framework
fastapi>=0.110
uvicorn[standard]>=0.27
python-multipart>=0.0.9
aiofiles>=23.2.0
```

- [ ] **Step 3: Instalar as novas dependências no ambiente virtual**

```bash
.venv/bin/pip install -r requirements.txt
```
Verificar saída: instalação bem-sucedida de `aiofiles`.

- [ ] **Step 4: Commit das alterações**

```bash
git add requirements.txt
git commit -m "chore: move frontend to directory and add aiofiles dependency"
```

---

### Task 2: Configurar Servimento Estático no FastAPI e Testes Unitários

**Files:**
- Create: `tests/test_server.py`
- Modify: `server.py:20-30`, `server.py:80-95`

**Interfaces:**
- Consumes: `frontend/index.html`, FastAPI app em `server.py`.
- Produces: Rota raiz `/` retornando `frontend/index.html`, rota `/health` mantida intacta.

- [ ] **Step 1: Escrever teste automatizado para as rotas do servidor**

Criar `tests/test_server.py`:
```python
import os
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Desativa carregamento real do modelo durante testes rápidos de rota
os.environ["PARAKEET_MODEL"] = "none"

from server import app


class ServerStaticFilesTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app, raise_server_exceptions=False)

    def test_root_serves_index_html(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))
        self.assertIn("Ditador por Voz", response.text)

    def test_health_endpoint_still_works(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
```

- [ ] **Step 2: Executar o teste e verificar que falha antes da implementação**

```bash
.venv/bin/python -m unittest tests/test_server.py
```
Esperado: FAIL (404 em `/` pois static files ainda não estão montados).

- [ ] **Step 3: Implementar o mount de `StaticFiles` no `server.py`**

Adicionar import:
```python
from fastapi.staticfiles import StaticFiles
```

Após os endpoints `@app.get("/health")` e `@app.post("/transcribe")`:
```python
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
```

- [ ] **Step 4: Reexecutar o teste unitário e verificar que passa**

```bash
.venv/bin/python -m unittest tests/test_server.py
```
Esperado: Ran 2 tests in ...s - OK.

- [ ] **Step 5: Commit das alterações**

```bash
git add server.py tests/test_server.py
git commit -m "feat: mount frontend static files in fastapi server"
```

---

### Task 3: Atualizar `frontend/index.html` para Detecção Dinâmica de Origem

**Files:**
- Modify: `frontend/index.html:79-85`

**Interfaces:**
- Consumes: `window.location.origin`.
- Produces: `SERVER_URL` padrão apontando dinamicamente para o mesmo host e porta do servidor.

- [ ] **Step 1: Atualizar a linha de configuração de `SERVER_URL` no `frontend/index.html`**

Substituir:
```javascript
let SERVER_URL = localStorage.getItem("parakeet_server_url") || "http://localhost:8765";
```
Por:
```javascript
let SERVER_URL = localStorage.getItem("parakeet_server_url") || (window.location.origin.startsWith("http") ? window.location.origin : "http://localhost:8765");
```

- [ ] **Step 2: Verificar a sintaxe e integridade do arquivo**

Garantir que a tag `<script>` permanece bem estruturada e sem erros de sintaxe.

- [ ] **Step 3: Commit das alterações**

```bash
git add frontend/index.html
git commit -m "fix(frontend): default server url to window.location.origin"
```

---

### Task 4: Atualizar `start.sh` e `README.md` com Inicialização Unificada

**Files:**
- Modify: `start.sh:35-44`
- Modify: `README.md:46-75`

**Interfaces:**
- Consumes: `$HOST`, `$PORT`, `$DISPLAY`, `$WAYLAND_DISPLAY`, `xdg-open`.
- Produces: Execução com comando único `./start.sh` e documentação atualizada.

- [ ] **Step 1: Adicionar rotina de abertura de navegador no `start.sh`**

Modificar a seção final de `start.sh`:
```bash
# 4) Sobe o servidor e abre o navegador se houver interface gráfica.
PORT="${PORT:-8765}"
HOST="${HOST:-127.0.0.1}"
URL="http://${HOST}:${PORT}"

echo
echo "🚀 Iniciando Parakeet V3 em ${URL}"
echo "   Para acessar, abra ${URL} no seu navegador."
echo "   Pressione Ctrl+C para encerrar."
echo

if command -v xdg-open >/dev/null 2>&1 && [ -n "${DISPLAY:-${WAYLAND_DISPLAY:-}}" ]; then
  (
    # Aguarda o servidor subir antes de abrir a aba
    sleep 2
    xdg-open "$URL" >/dev/null 2>&1 || true
  ) &
fi

HOST="$HOST" PORT="$PORT" python server.py
```

- [ ] **Step 2: Atualizar o `README.md` removendo referências a `python3 -m http.server 8080`**

Atualizar as seções "Como rodar" e "Estrutura" para refletir o comando único:
```bash
./start.sh
```
E explicar que o backend e frontend rodam juntos em `http://127.0.0.1:8765`.

- [ ] **Step 3: Validar a sintaxe do script de inicialização**

```bash
bash -n start.sh
```
Esperado: código de retorno 0 (sem erros de sintaxe).

- [ ] **Step 4: Commit das alterações**

```bash
git add start.sh README.md
git commit -m "feat(cli): unify startup script and update documentation"
```
