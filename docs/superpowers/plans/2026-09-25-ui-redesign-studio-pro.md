# UI Redesign Studio Pro Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transformar a interface web do nohands em uma aplicação estilo Studio Pro / Linear Dark, substituindo a estética genérica de "IA Slop" por uma paleta escura profunda, topbar limpa com status pill e popover, hero de gravação neon, editor com toolbar integrada e contador de palavras/caracteres, toasts flutuantes e timeline de histórico com ícones SVG inline.

**Architecture:** A interface inteira permanece em `frontend/index.html` com zero dependências externas (100% autônoma e offline-ready). O CSS utiliza tokens modernos em `:root` com efeitos sutis de iluminação e bordas finas translúcidas. Os emojis são substituídos por ícones SVG vetoriais inline. O painel técnico de URL do servidor é movido para um popover ativado pelo status pill no cabeçalho. Toasts flutuantes substituem alertas nativos.

**Tech Stack:** Vanilla HTML5, CSS3 moderno (Custom Properties, Flexbox, Grid, transitions), Vanilla JavaScript (ES6+), Web Audio API, Canvas 2D, Python `unittest`.

## Global Constraints

- Zero dependências externas (sem CDN, sem bibliotecas JS externas, sem Tailwind compilado).
- Preservar 100% dos IDs existentes para retrocompatibilidade com testes e automações:
  - `#vuContainer`, `#vuMeter`, `#recordBtn`, `#output`, `#status`, `#serverUrl`, `#serverDot`, `#checkBtn`, `#fileInput`
  - `#historySection`, `#historyList`, `#historyCount`, `#clearHistoryBtn`
  - Funções: `initAudioVisualizer`, `stopAudioVisualizer`, `loadHistory`, `saveHistory`, `addHistoryEntry`, `deleteHistoryEntry`, `clearAllHistory`, `renderHistory`
- Todos os testes automatizados devem passar com código de saída 0.

---

### Task 1: Atualizar Testes Automatizados com Elementos do Studio Pro

**Files:**
- Modify: `tests/test_frontend.py`

**Interfaces:**
- Produces: Testes unitários para validar a presença de novos elementos Studio Pro: `#toastContainer`, `#wordCharCount`, `#settingsPopover`, `#settingsBtn`.

- [ ] **Step 1: Adicionar novos testes em `tests/test_frontend.py`**

Modificar `tests/test_frontend.py`:
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

    def test_studio_pro_elements_present(self):
        """Verifica se os novos elementos do design Studio Pro estão presentes."""
        self.assertIn('id="toastContainer"', self.content, "Container de toasts deve existir")
        self.assertIn('id="wordCharCount"', self.content, "Contador de palavras/caracteres deve existir")
        self.assertIn('id="settingsPopover"', self.content, "Popover de conexão deve existir")
        self.assertIn('id="settingsBtn"', self.content, "Botão acionador de configurações deve existir")
        self.assertIn('showToast', self.content, "Função showToast deve existir")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Executar teste para verificar falha TDD esperada**

Run: `.venv/bin/python -m unittest tests/test_frontend.py -k test_studio_pro_elements_present`
Expected: FAIL (pois os novos IDs ainda não foram implementados no HTML).

- [ ] **Step 3: Commitar a atualização de testes**

```bash
git add tests/test_frontend.py
git commit -m "test: add tests for studio pro ui elements and functions"
```

---

### Task 2: Implementar Design System Studio Pro, Topbar e Status Popover

**Files:**
- Modify: `frontend/index.html`

**Interfaces:**
- Produces:
  - Tokens CSS em `:root` (paleta `#07090e`, `#0e1322`, `#161f36`, iluminação neon, tipografia refinada).
  - Header com logotipo estilizado e Status Pill (`#settingsBtn`).
  - Popover flutuante de configurações (`#settingsPopover`) contendo `#serverUrl`, `#checkBtn`, `#serverDot`, e `#status`.
  - Função `toggleSettingsPopover()`.

- [ ] **Step 1: Atualizar bloco `<style>` com os Tokens e layout Studio Pro**

Configurar em `frontend/index.html` o design system:
```css
    :root {
      --bg: #07090e;
      --surface: #0e1322;
      --surface-elevated: #141c30;
      --surface-hover: #1c2744;
      --border: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(56, 189, 248, 0.4);
      --primary: #38bdf8;
      --primary-glow: rgba(56, 189, 248, 0.25);
      --rec: #ef4444;
      --rec-glow: rgba(239, 68, 68, 0.35);
      --ok: #10b981;
      --text: #f1f5f9;
      --muted: #94a3b8;
    }
```
Adicionar estilos para a topbar, logo, status pill flutuante e modal popover de conexão com backdrop sutil.

- [ ] **Step 2: Implementar o HTML da Topbar e do Popover de Conexão**

Estruturar no início do `<body>`:
```html
  <header class="topbar">
    <div class="brand">
      <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"/>
      </svg>
      <span class="brand-name">nohands</span>
      <span class="brand-tag">local speech studio</span>
    </div>
    
    <div class="topbar-actions">
      <button id="settingsBtn" class="status-pill" onclick="toggleSettingsPopover()">
        <span class="dot" id="serverDot"></span>
        <span id="statusShort">Verificando...</span>
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
      </button>

      <div id="settingsPopover" class="popover">
        <div class="popover-title">Conexão do Servidor</div>
        <div class="server-row">
          <input type="text" id="serverUrl" value="http://localhost:8765" placeholder="http://localhost:8765" />
          <button onclick="checkServer()" id="checkBtn" class="btn-primary-sm">Conectar</button>
        </div>
        <div id="status" class="status-detail">Verificando backend...</div>
      </div>
    </div>
  </header>
```

- [ ] **Step 3: Implementar a lógica de alternância do Popover e atualização de status**

No script de `frontend/index.html`:
```javascript
    function toggleSettingsPopover() {
      const popover = document.getElementById("settingsPopover");
      if (popover) popover.classList.toggle("open");
    }

    // Fecha o popover ao clicar fora
    document.addEventListener("click", (e) => {
      const popover = document.getElementById("settingsPopover");
      const btn = document.getElementById("settingsBtn");
      if (popover && btn && !popover.contains(e.target) && !btn.contains(e.target)) {
        popover.classList.remove("open");
      }
    });
```
Atualizar `checkServer()` para sincronizar tanto `#status` quanto o `#statusShort` na pílula do topo (`Parakeet V3 Ready` ou `Offline`).

- [ ] **Step 4: Commitar as alterações da Topbar**

```bash
git add frontend/index.html
git commit -m "feat(frontend): implement studio pro design tokens, topbar and status popover"
```

---

### Task 3: Implementar Hero de Gravação Neon, VU Meter e Sistema de Toasts

**Files:**
- Modify: `frontend/index.html`

**Interfaces:**
- Produces:
  - Botão pílula `#recordBtn` com pulso neon.
  - `#vuContainer` e `#vuMeter` com barras gradientes neon de alta densidade e transição suave.
  - Container flutuante `#toastContainer` e função `showToast(msg, type)`.

- [ ] **Step 1: Estilizar o botão Hero com pulso e anel neon**

Estilos para `#recordBtn` em `frontend/index.html`:
- Formato pílula estilizado com ícone SVG de microfone inline.
- Animação `@keyframes pulseRing` que irradia quando `appState === 'recording'`.
- Badge de atalho `<kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>Espaço</kbd>` abaixo do botão.

- [ ] **Step 2: Aprimorar o Canvas do VU Meter**

- Redesenhar barras no `drawAudioVisualizer`: 24 barras com largura equilibrada, gradiente neon `#10b981` ➔ `#38bdf8` ➔ `#ef4444`.
- Transição suave de altura quando a gravação é acionada/pausada.

- [ ] **Step 3: Implementar o Sistema de Toasts Flutuantes**

Inserir no final do HTML:
```html
  <div id="toastContainer" class="toast-container"></div>
```
Implementar função JavaScript:
```javascript
    function showToast(message, type = "info") {
      const container = document.getElementById("toastContainer");
      if (!container) return;
      const toast = document.createElement("div");
      toast.className = `toast toast-${type}`;
      toast.textContent = message;
      container.appendChild(toast);
      setTimeout(() => {
        toast.classList.add("fade-out");
        setTimeout(() => toast.remove(), 300);
      }, 3000);
    }
```
Substituir chamadas de `alert()` e atualizações secundárias de texto por `showToast(msg, 'success'|'error'|'info')`.

- [ ] **Step 4: Commitar melhorias do Hero, VU Meter e Toasts**

```bash
git add frontend/index.html
git commit -m "feat(frontend): implement hero recording button with pulse, neon vu meter and toast system"
```

---

### Task 4: Implementar Card do Editor Pro com Toolbar Integrada, Contador e Timeline

**Files:**
- Modify: `frontend/index.html`

**Interfaces:**
- Produces:
  - Card integrado com `#output` e toolbar inferior acoplada.
  - Ícones SVG inline para Copiar, Baixar .txt, Subir Áudio e Limpar.
  - Contador `#wordCharCount` atualizado dinamicamente.
  - Timeline de Histórico redesenhada com ícones SVG.

- [ ] **Step 1: Estruturar o Card do Editor com Toolbar e Contador**

```html
  <div class="editor-card">
    <textarea id="output" placeholder="O texto transcrito aparecerá aqui..."></textarea>
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <button class="tool-btn" onclick="copyToClipboard()" title="Copiar texto">
          <svg class="tool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
          <span>Copiar</span>
        </button>
        <button class="tool-btn" onclick="downloadTxt()" title="Baixar .txt">
          <svg class="tool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          <span>Baixar .txt</span>
        </button>
        <label class="tool-btn file-btn" title="Transcrever arquivo de áudio">
          <svg class="tool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/></svg>
          <span>Subir Áudio</span>
          <input type="file" id="fileInput" accept="audio/*" style="display:none" />
        </label>
        <button class="tool-btn danger" onclick="clearOutput()" title="Limpar editor">
          <svg class="tool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
          <span>Limpar</span>
        </button>
      </div>
      <div id="wordCharCount" class="counter">0 palavras • 0 caracteres</div>
    </div>
  </div>
```

- [ ] **Step 2: Implementar lógica do contador de palavras e caracteres**

```javascript
    function updateWordCharCount() {
      const text = outputEl.value.trim();
      const chars = outputEl.value.length;
      const words = text ? text.split(/\s+/).length : 0;
      const counterEl = document.getElementById("wordCharCount");
      if (counterEl) {
        counterEl.textContent = `${words} ${words === 1 ? 'palavra' : 'palavras'} • ${chars} ${chars === 1 ? 'caractere' : 'caracteres'}`;
      }
    }
    outputEl.addEventListener("input", updateWordCharCount);
```
Chamar `updateWordCharCount()` ao transcrever, inserir do histórico ou limpar o editor.

- [ ] **Step 3: Redesenhar os cards de Histórico com visual de Timeline e Ícones SVG**

Atualizar `renderHistory()` para gerar os cards com botões vetoriais discretos (Copiar, Inserir, Excluir) e timestamp refinado.

- [ ] **Step 4: Executar testes automatizados do frontend**

Run: `.venv/bin/python -m unittest tests/test_frontend.py`
Expected: PASS (todos os testes, incluindo os novos do Studio Pro, passando 100%).

- [ ] **Step 5: Commitar a reformulação do Editor e Histórico**

```bash
git add frontend/index.html
git commit -m "feat(frontend): implement studio pro editor card, live counter and timeline history"
```

---

### Task 5: Verificação Completa e Atualização da Documentação

**Files:**
- Modify: `README.md`
- Test: Todas as suítes de testes em `tests/`

- [ ] **Step 1: Executar suíte completa de testes unitários**

Run: `.venv/bin/python -m unittest discover tests`
Expected: PASS.

- [ ] **Step 2: Atualizar `README.md` destacando a nova interface Studio Pro**

- [ ] **Step 3: Commitar documentação**

```bash
git add README.md
git commit -m "docs: update readme with studio pro ui details"
```
