# Especificação Técnica: Unificação da Execução (Servidor FastAPI + Frontend)

**Data:** 2026-09-25  
**Status:** Aprovado  
**Objetivo:** Permitir a execução completa da aplicação (backend + frontend) através de um único comando (`./start.sh`), eliminando a necessidade de um segundo terminal com servidor HTTP auxiliar.

---

## 1. Contexto e Motivação

Atualmente, o projeto exige a execução de dois processos separados em dois terminais distintos:
1. `start.sh` (executa `server.py` via FastAPI na porta `8765`).
2. `python3 -m http.server 8080` para servir `index.html`.

Essa divisão adiciona atrito operacional, obriga o usuário a gerenciar duas portas e requer configuração manual de CORS no frontend caso a URL mude.

---

## 2. Arquitetura Proposta

### 2.1 Estrutura de Diretórios
Os arquivos estáticos serão organizados em um diretório dedicado:

```text
parakeet-ditado/
├── frontend/
│   └── index.html             # Interface web servida pelo backend
├── server.py                  # Servidor FastAPI com rotas de API e mount estático
├── start.sh                   # Script único de inicialização com auto-open
├── requirements.txt           # Adição de aiofiles para servimento estático assíncrono
├── README.md                  # Documentação atualizada
└── .gitignore                 # Configuração de arquivos ignorados
```

O arquivo `como rodar.txt` será removido, centralizando todas as instruções no `README.md`.

---

## 3. Detalhamento dos Componentes

### 3.1 Backend (`server.py`)
- Importar `StaticFiles` de `starlette.staticfiles` ou `fastapi.staticfiles`.
- Utilizar caminho absoluto resolvido a partir do arquivo (`Path(__file__).parent / "frontend"`).
- Registrar os endpoints de API primeiro (`/health` e `/transcribe`).
- Montar os arquivos estáticos na raiz após as rotas:
  ```python
  frontend_dir = Path(__file__).parent / "frontend"
  app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
  ```

### 3.2 Dependências (`requirements.txt`)
- Adicionar `aiofiles>=23.2.0` (requisito do FastAPI/Starlette para leitura não-bloqueante de arquivos estáticos).

### 3.3 Frontend (`frontend/index.html`)
- Alterar a obtenção inicial da URL do servidor:
  ```javascript
  let SERVER_URL = localStorage.getItem("parakeet_server_url") || window.location.origin;
  ```
- O restante da lógica de gravação e envio de áudio para `/transcribe` e verificação em `/health` permanece inalterado e compatível.

### 3.4 Script de Inicialização (`start.sh`)
- Manter as verificações de `ffmpeg` e criação do ambiente virtual `.venv`.
- Após a mensagem de inicialização, disparar uma rotina em background que:
  1. Aguarda brevemente a porta ficar acessível (`curl` ou `sleep 1`).
  2. Caso exista ambiente gráfico (`$DISPLAY` ou `$WAYLAND_DISPLAY`) e utilitário `xdg-open`, abre automaticamente a URL `http://${HOST}:${PORT}` no navegador padrão sem travar a execução.
- Iniciar `server.py` com o Uvicorn.

---

## 4. Tratamento de Erros e Casos de Borda

1. **Tentativa de abertura de navegador sem ambiente gráfico**:
   - O `start.sh` verifica a existência de `$DISPLAY` / `$WAYLAND_DISPLAY` e `command -v xdg-open`. Se não houver, apenas imprime a URL no terminal sem emitir erro.
2. **Prioridade de Rotas da API**:
   - O mount estático na raiz (`/`) deve vir estritamente após a definição dos métodos `@app.get("/health")` e `@app.post("/transcribe")` para não interceptar as requisições da API.
3. **Resolução de Caminhos**:
   - Uso de `Path(__file__).parent / "frontend"` garante funcionamento mesmo se o script for invocado a partir de outro diretório de trabalho.

---

## 5. Critérios de Aceite

1. O comando `./start.sh` inicia o backend e o frontend simultaneamente.
2. Acessar `http://127.0.0.1:8765` no navegador carrega a interface de transcrição.
3. O status do servidor no frontend marca `✅ Servidor online`.
4. Uma gravação ou envio de áudio para transcrição funciona normalmente na mesma porta.
5. Nenhum segundo terminal com `http.server` é necessário.
