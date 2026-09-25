# Interface e Usabilidade: VU Meter e Histórico Local Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar visualizador de áudio em tempo real (VU Meter via Web Audio API e Canvas) e histórico local de transcrições (`localStorage` com limite de 50 itens, cópia, inserção e exclusão) na interface web do nohands (`frontend/index.html`).

**Architecture:** O visualizador de áudio conecta-se ao `MediaStream` do microfone via `AudioContext` e `AnalyserNode`, renderizando barras de nível em um `<canvas>` durante a gravação com cancelamento automático ao parar. O histórico local persiste as transcrições em `localStorage` sob a chave `parakeet_transcription_history`, gerando cards interativos com ações de cópia, inserção no editor principal e exclusão.

**Tech Stack:** Vanilla JavaScript (ES6+), HTML5 Canvas 2D, Web Audio API, CSS3, Python `unittest` e FastAPI `TestClient`.

## Global Constraints

- Zero dependências externas (sem bibliotecas externas ou CDNs; 100% autossuficiente e offline).
- Preservar integridade visual Dark Mode existente (paleta Slate: `#0f172a`, `#1e293b`, `#334155`, `#3b82f6`, `#10b981`).
- O nó do analisador de áudio **nunca** deve se conectar a `audioCtx.destination` para evitar microfonia/feedback.
- Limite máximo estrito de 50 registros no `localStorage` (estratégia FIFO).
- Todos os testes automatizados devem passar com código de saída 0.

---

### Task 1: Criar Testes Automatizados de Validação do Frontend

**Files:**
- Create: `tests/test_frontend.py`
- Modify: `tests/test_server.py`

**Interfaces:**
- Produces: Testes unitários para validar a estrutura HTML, presença de IDs essenciais (`vuMeter`, `historyContainer`, `historyList`, etc.) e funções Javascript esperadas no arquivo `frontend/index.html`.

- [ ] **Step 1: Escrever teste automatizado para estrutura do frontend**

Criar `tests/test_frontend.py`:
```python
import os
import unittest

class TestFrontendStructure(unittest.TestCase):
    def setUp(self):
        self.html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
        self.assertTrue(os.path.exists(self.html_path), "frontend/index.html deve existir")
        with open(self.html_path, "r", encoding="utf-8") as f:
            self.content = f.read()

    def test_vu_meter_elements_present(self):
        """Verifica se os elementos e funções do VU meter estão declarados no frontend."""
        self.assertIn('id="vuContainer"', self.content, "Container do VU meter deve existir")
        self.assertIn('id="vuMeter"', self.content, "Canvas do VU meter deve existir")
        self.assertIn('initAudioVisualizer', self.content, "Função initAudioVisualizer deve existir")
        self.assertIn('stopAudioVisualizer', self.content, "Função stopAudioVisualizer deve existir")

    def test_history_elements_present(self):
        """Verifica se os elementos e funções do histórico estão declarados no frontend."""
        self.assertIn('id="historySection"', self.content, "Seção de histórico deve existir")
        self.assertIn('id="historyList"', self.content, "Lista de histórico deve existir")
        self.assertIn('id="historyCount"', self.content, "Contador de histórico deve existir")
        self.assertIn('parakeet_transcription_history', self.content, "Chave de localStorage correta deve existir")
        self.assertIn('addHistoryEntry', self.content, "Função addHistoryEntry deve existir")
        self.assertIn('deleteHistoryEntry', self.content, "Função deleteHistoryEntry deve existir")
        self.assertIn('clearAllHistory', self.content, "Função clearAllHistory deve existir")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Executar teste para verificar falha esperada**

Run: `.venv/bin/python -m unittest tests/test_frontend.py`
Expected: FAIL (pois `vuContainer`, `historySection`, etc. ainda não foram adicionados ao `frontend/index.html`).

- [ ] **Step 3: Commitar a suíte de testes de validação**

```bash
git add tests/test_frontend.py
git commit -m "test: add frontend structure and interface tests"
```

---

### Task 2: Implementar o Visualizador de Áudio (VU Meter)

**Files:**
- Modify: `frontend/index.html`

**Interfaces:**
- Consumes: `stream` de áudio capturado pelo `getUserMedia`.
- Produces:
  - `<div id="vuContainer" class="vu-container"><canvas id="vuMeter" height="36"></canvas></div>`
  - `initAudioVisualizer(stream)`: Inicializa `AudioContext` e `AnalyserNode`, iniciando loop de desenho no canvas.
  - `stopAudioVisualizer()`: Para loop de animação, fecha `AudioContext` e limpa canvas.

- [ ] **Step 1: Adicionar estilos CSS e elemento HTML do VU Meter**

No arquivo `frontend/index.html`:
Adicionar estilos no bloco `<style>`:
```css
    .vu-container { width: 100%; height: 42px; background: #0b1120; border: 1px solid #334155; border-radius: 8px; margin-bottom: 0.8rem; display: none; align-items: center; justify-content: center; padding: 4px 8px; overflow: hidden; transition: all 0.2s ease; }
    .vu-container.active { display: flex; }
    #vuMeter { width: 100%; height: 100%; display: block; }
```

Inserir o elemento HTML entre `#recordBtn` e `#output`:
```html
    <div id="vuContainer" class="vu-container">
      <canvas id="vuMeter" width="600" height="34"></canvas>
    </div>
```

- [ ] **Step 2: Implementar a lógica JavaScript do VU Meter**

No script de `frontend/index.html`:
Definir variáveis de estado do visualizador:
```javascript
    let audioCtx = null;
    let analyserNode = null;
    let visualizerSource = null;
    let visualizerAnimId = null;
    const vuContainer = document.getElementById("vuContainer");
    const vuCanvas = document.getElementById("vuMeter");
    const vuCtx = vuCanvas ? vuCanvas.getContext("2d") : null;
```

Implementar funções:
```javascript
    function initAudioVisualizer(audioStream) {
      try {
        window.AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!window.AudioContext) return;
        audioCtx = new AudioContext();
        analyserNode = audioCtx.createAnalyser();
        analyserNode.fftSize = 64;
        analyserNode.smoothingTimeConstant = 0.8;
        visualizerSource = audioCtx.createMediaStreamSource(audioStream);
        visualizerSource.connect(analyserNode);

        if (vuContainer) vuContainer.classList.add("active");
        drawAudioVisualizer();
      } catch (err) {
        console.warn("[VU Meter] Falha ao iniciar visualizador:", err);
      }
    }

    function drawAudioVisualizer() {
      if (!analyserNode || !vuCtx) return;
      const bufferLength = analyserNode.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      analyserNode.getByteFrequencyData(dataArray);

      vuCtx.clearRect(0, 0, vuCanvas.width, vuCanvas.height);
      const barCount = 20;
      const totalWidth = vuCanvas.width;
      const barSpacing = 4;
      const barWidth = (totalWidth - (barCount - 1) * barSpacing) / barCount;
      const height = vuCanvas.height;

      for (let i = 0; i < barCount; i++) {
        const dataIdx = Math.floor(i * (bufferLength / barCount));
        const val = dataArray[dataIdx] || 0;
        const barHeight = Math.max(4, (val / 255) * height);
        const x = i * (barWidth + barSpacing);
        const y = height - barHeight;

        const grad = vuCtx.createLinearGradient(0, height, 0, 0);
        grad.addColorStop(0, "#10b981");
        grad.addColorStop(0.6, "#3b82f6");
        grad.addColorStop(1, "#ef4444");

        vuCtx.fillStyle = grad;
        vuCtx.beginPath();
        vuCtx.roundRect(x, y, barWidth, barHeight, 3);
        vuCtx.fill();
      }

      visualizerAnimId = requestAnimationFrame(drawAudioVisualizer);
    }

    function stopAudioVisualizer() {
      if (visualizerAnimId) {
        cancelAnimationFrame(visualizerAnimId);
        visualizerAnimId = null;
      }
      if (visualizerSource) {
        try { visualizerSource.disconnect(); } catch (_) {}
        visualizerSource = null;
      }
      if (audioCtx) {
        try { audioCtx.close(); } catch (_) {}
        audioCtx = null;
      }
      analyserNode = null;
      if (vuContainer) vuContainer.classList.remove("active");
      if (vuCtx) vuCtx.clearRect(0, 0, vuCanvas.width, vuCanvas.height);
    }
```

- [ ] **Step 3: Conectar ciclo de vida no `startRecording` e `stopRecording`**

Em `startRecording()`:
Logo após iniciar o MediaRecorder, chamar: `initAudioVisualizer(stream);`

Em `stopRecording()` e `mediaRecorder.onstop`:
Chamar: `stopAudioVisualizer();`

- [ ] **Step 4: Executar validação parcial dos testes**

Run: `.venv/bin/python -m unittest tests/test_frontend.py -k test_vu_meter_elements_present`
Expected: PASS

- [ ] **Step 5: Commitar a implementação do VU Meter**

```bash
git add frontend/index.html
git commit -m "feat(frontend): implement real-time audio visualizer vu meter"
```

---

### Task 3: Implementar o Histórico Local de Transcrições

**Files:**
- Modify: `frontend/index.html`

**Interfaces:**
- Consumes: Texto transcrito retornado por `transcribeBlob()`.
- Produces:
  - `<div id="historySection">...</div>`
  - Métodos: `loadHistory()`, `saveHistory(items)`, `addHistoryEntry(text)`, `deleteHistoryEntry(id)`, `clearAllHistory()`, `copyHistoryText(id)`, `insertHistoryText(id)`, `renderHistory()`.

- [ ] **Step 1: Adicionar estilos CSS do painel de histórico**

No arquivo `frontend/index.html`:
Adicionar estilos no `<style>`:
```css
    .history-section { margin-top: 1.2rem; border-top: 1px solid #334155; padding-top: 1rem; }
    .history-header { display: flex; justify-content: space-between; align-items: center; cursor: pointer; user-select: none; margin-bottom: 0.6rem; }
    .history-title { font-size: 0.95rem; font-weight: 600; color: var(--text); display: flex; align-items: center; gap: 0.4rem; }
    .badge { background: #334155; color: var(--text); padding: 2px 7px; border-radius: 10px; font-size: 0.75rem; }
    .history-actions { display: flex; gap: 0.4rem; }
    .history-list { max-height: 250px; overflow-y: auto; display: flex; flex-direction: column; gap: 0.5rem; padding-right: 4px; }
    .history-list::-webkit-scrollbar { width: 6px; }
    .history-list::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
    .history-item { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 0.7rem; font-size: 0.9rem; }
    .history-item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem; font-size: 0.75rem; color: var(--muted); }
    .history-item-text { color: var(--text); line-height: 1.4; word-break: break-word; white-space: pre-wrap; margin-bottom: 0.5rem; }
    .history-item-btns { display: flex; gap: 0.4rem; justify-content: flex-end; }
    .btn-sm { padding: 3px 8px; font-size: 0.75rem; border-radius: 4px; background: #334155; }
    .empty-history { text-align: center; color: var(--muted); font-size: 0.85rem; padding: 1rem; }
```

- [ ] **Step 2: Adicionar elemento HTML do Histórico**

Inserir logo após os botões de utilitários no `frontend/index.html`:
```html
    <div id="historySection" class="history-section">
      <div class="history-header" onclick="toggleHistoryAccordion()">
        <div class="history-title">
          <span>📜 Histórico de Transcrições</span>
          <span id="historyCount" class="badge">0</span>
          <span id="historyToggleIcon">▼</span>
        </div>
        <div class="history-actions">
          <button id="clearHistoryBtn" class="btn-sm" onclick="event.stopPropagation(); clearAllHistory();" title="Limpar todo o histórico">🧹 Limpar</button>
        </div>
      </div>
      <div id="historyList" class="history-list">
        <div class="empty-history">Nenhuma transcrição no histórico ainda.</div>
      </div>
    </div>
```

- [ ] **Step 3: Implementar funções JavaScript de Histórico**

No script de `frontend/index.html`:
```javascript
    const HISTORY_STORAGE_KEY = "parakeet_transcription_history";
    const MAX_HISTORY_ITEMS = 50;
    let historyExpanded = true;

    function toggleHistoryAccordion() {
      historyExpanded = !historyExpanded;
      const listEl = document.getElementById("historyList");
      const iconEl = document.getElementById("historyToggleIcon");
      if (listEl) listEl.style.display = historyExpanded ? "flex" : "none";
      if (iconEl) iconEl.textContent = historyExpanded ? "▼" : "▶";
    }

    function loadHistory() {
      try {
        const raw = localStorage.getItem(HISTORY_STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
      } catch (err) {
        console.warn("[Histórico] Erro ao carregar histórico:", err);
        return [];
      }
    }

    function saveHistory(items) {
      try {
        const trimmed = items.slice(0, MAX_HISTORY_ITEMS);
        localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(trimmed));
      } catch (err) {
        console.warn("[Histórico] Erro ao salvar histórico:", err);
      }
    }

    function addHistoryEntry(text) {
      const cleanText = (text || "").trim();
      if (!cleanText) return;
      const items = loadHistory();
      const newEntry = {
        id: "hist_" + Date.now() + "_" + Math.random().toString(36).substr(2, 4),
        timestamp: new Date().toISOString(),
        text: cleanText
      };
      items.unshift(newEntry);
      saveHistory(items);
      renderHistory();
    }

    function deleteHistoryEntry(id) {
      const items = loadHistory().filter(item => item.id !== id);
      saveHistory(items);
      renderHistory();
    }

    function clearAllHistory() {
      const items = loadHistory();
      if (items.length === 0) return;
      if (confirm("Deseja realmente apagar todo o histórico de transcrições?")) {
        localStorage.removeItem(HISTORY_STORAGE_KEY);
        renderHistory();
        statusEl.textContent = "🧹 Histórico apagado.";
      }
    }

    async function copyHistoryText(id, btnElement) {
      const items = loadHistory();
      const target = items.find(item => item.id === id);
      if (!target) return;
      try {
        await navigator.clipboard.writeText(target.text);
        if (btnElement) {
          const original = btnElement.textContent;
          btnElement.textContent = "✅ Copiado!";
          setTimeout(() => { btnElement.textContent = original; }, 1200);
        }
      } catch {
        alert("Falha ao copiar texto do histórico.");
      }
    }

    function insertHistoryText(id) {
      const items = loadHistory();
      const target = items.find(item => item.id === id);
      if (!target) return;
      if (outputEl.value) outputEl.value += " ";
      outputEl.value += target.text;
      statusEl.textContent = "➕ Texto anexado ao editor.";
    }

    function renderHistory() {
      const listEl = document.getElementById("historyList");
      const countEl = document.getElementById("historyCount");
      if (!listEl || !countEl) return;

      const items = loadHistory();
      countEl.textContent = items.length;

      if (items.length === 0) {
        listEl.innerHTML = '<div class="empty-history">Nenhuma transcrição no histórico ainda.</div>';
        return;
      }

      listEl.innerHTML = "";
      items.forEach(item => {
        const itemEl = document.createElement("div");
        itemEl.className = "history-item";

        const dateObj = new Date(item.timestamp);
        const dateStr = isNaN(dateObj.getTime()) ? item.timestamp : dateObj.toLocaleString("pt-BR");

        const headerEl = document.createElement("div");
        headerEl.className = "history-item-header";
        headerEl.innerHTML = `<span>🕒 ${dateStr}</span>`;

        const textEl = document.createElement("div");
        textEl.className = "history-item-text";
        textEl.textContent = item.text;

        const btnsEl = document.createElement("div");
        btnsEl.className = "history-item-btns";

        const copyBtn = document.createElement("button");
        copyBtn.className = "btn-sm";
        copyBtn.textContent = "📋 Copiar";
        copyBtn.onclick = () => copyHistoryText(item.id, copyBtn);

        const insertBtn = document.createElement("button");
        insertBtn.className = "btn-sm";
        insertBtn.textContent = "➕ Inserir";
        insertBtn.onclick = () => insertHistoryText(item.id);

        const deleteBtn = document.createElement("button");
        deleteBtn.className = "btn-sm";
        deleteBtn.textContent = "🗑️ Excluir";
        deleteBtn.onclick = () => deleteHistoryEntry(item.id);

        btnsEl.appendChild(copyBtn);
        btnsEl.appendChild(insertBtn);
        btnsEl.appendChild(deleteBtn);

        itemEl.appendChild(headerEl);
        itemEl.appendChild(textEl);
        itemEl.appendChild(btnsEl);

        listEl.appendChild(itemEl);
      });
    }
```

- [ ] **Step 4: Integrar adição automática no `transcribeBlob` e inicialização no boot**

Em `transcribeBlob`:
Após receber `text`:
```javascript
      if (outputEl.value) outputEl.value += " ";
      outputEl.value += text;
      addHistoryEntry(text);
```

No final do script (boot):
Chamar `renderHistory();` logo após `checkServer();`.

- [ ] **Step 5: Executar teste automatizado do frontend**

Run: `.venv/bin/python -m unittest tests/test_frontend.py`
Expected: PASS (todos os testes de estrutura e funções devem passar).

- [ ] **Step 6: Commitar implementação do histórico local**

```bash
git add frontend/index.html
git commit -m "feat(frontend): implement local transcription history with actions"
```

---

### Task 4: Verificação Completa e Atualização da Documentação

**Files:**
- Modify: `README.md`
- Test: Todas as suítes de testes em `tests/`

- [ ] **Step 1: Executar suíte completa de testes unitários**

Run: `.venv/bin/python -m unittest discover tests`
Expected: PASS (todos os testes passando sem erros).

- [ ] **Step 2: Atualizar `README.md` documentando os novos recursos**

Atualizar a seção de Funcionalidades no `README.md` mencionando:
- VU Meter animado em tempo real via Web Audio API.
- Histórico local persistente (`localStorage`) com ações de Copiar, Inserir no editor e Excluir.

- [ ] **Step 3: Commitar documentação atualizada**

```bash
git add README.md
git commit -m "docs: update readme with vu meter and transcription history features"
```
