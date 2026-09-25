# Design Spec: Interface e Usabilidade (VU Meter e Histórico Local)

- **Data**: 2026-09-25
- **Status**: Aprovado para Implementação
- **Autor**: Robson Paulo / Pair Programming com Antigravity

---

## 1. Visão Geral e Objetivos

O projeto **nohands** (transcrição de voz local com modelo NVIDIA Parakeet V3) concluiu a unificação da execução na Fase 1. A Fase 2 tem como objetivo aprimorar a interface de usuário (UI) e a usabilidade (UX), entregando dois recursos principais:

1. **Visualizador de Áudio em Tempo Real (VU Meter):**
   - Fornecer feedback visual imediato de que o microfone está captando som enquanto o usuário dita.
   - Evitar dúvidas sobre se o microfone está mudo ou se o navegador está capturando áudio.

2. **Histórico Local de Transcrições (`localStorage`):**
   - Registrar automaticamente as transcrições finalizadas com data e hora.
   - Permitir ao usuário recuperar, copiar ou reutilizar trechos transcritos sem risco de perda de dados ao recarregar a página ou ao limpar o editor principal.

---

## 2. Requisitos e Restrições

### 2.1 Requisitos Funcionais
- **RF01 - Visualização de Áudio (VU Meter):**
  - Conectar ao `MediaStream` ativo durante a gravação via Web Audio API.
  - Desenhar de 16 a 20 barras de frequência em um elemento `<canvas id="vuMeter">` em tempo real (`requestAnimationFrame`).
  - O visualizador deve aparecer suavemente apenas enquanto `appState === 'recording'` e recolher/ocultar quando a gravação parar ou o sistema estiver inativo/processando.
  - O áudio analisado **não** deve ser roteado para a saída de som (`destination`) para prevenir microfonia ou eco.
- **RF02 - Armazenamento de Histórico Local:**
  - Persistir as transcrições em `localStorage` sob a chave `parakeet_transcription_history`.
  - Cada registro deve conter `{ id: string, timestamp: string, text: string }`.
  - Limite máximo de retenção: **50 registros mais recentes** (estratégia FIFO para o excedente).
- **RF03 - Painel e Ações do Histórico:**
  - Painel posicionado abaixo dos botões de utilitários no `frontend/index.html`.
  - Cabeçalho expansível/retrátil com contador total de itens salvos e botão "Limpar Histórico" (com confirmação `confirm()`).
  - Lista com rolagem suave (`max-height: 250px`).
  - Cada card deve exibir a data/hora formatada em PT-BR (ex: `25/09/2026 12:05:30`), o texto transcrito, e 3 ações rápidas:
    - 📋 **Copiar**: Copia o texto para o clipboard com feedback visual ("Copiado!").
    - ➕ **Inserir**: Anexa o texto ao editor `textarea` principal.
    - 🗑️ **Excluir**: Remove o item individualmente do `localStorage` e da interface.
- **RF04 - Inclusão Automática:**
  - Transcrições concluídas com sucesso (tanto via gravação de microfone quanto via upload de arquivo de áudio) devem ser salvas automaticamente no histórico.

### 2.2 Requisitos Não-Funcionais
- **Zero Dependências Externas:** O frontend deve continuar funcionando de maneira 100% autônoma, sem requisições a CDNs ou bibliotecas JS/CSS externas.
- **Performance e Eficiência de Recursos:**
  - O `AudioContext` e a animação do canvas devem ser encerrados/cancelados assim que a gravação for finalizada para não gastar CPU em segundo plano.
  - O `localStorage` armazena apenas metadados leves e texto, evitando consumo excessivo de memória.
- **Design System Coerente:** Seguir rigorosamente o padrão visual Dark Mode existente (Slate Tailwind: `#0f172a`, `#1e293b`, `#334155`, detalhes `#3b82f6` e `#10b981`).

---

## 3. Arquitetura e Detalhamento dos Componentes

### 3.1 Pipeline de Áudio e Canvas (VU Meter)
```
[Microfone (MediaStream)]
       │
       ▼
 [AudioContext]
       │
       ▼
[AnalyserNode (fftSize=64)]  ── (getByteFrequencyData) ──►  [requestAnimationFrame]
  (SEM conexão ao destination!)                                     │
                                                                   ▼
                                                       [Canvas 2D: Desenho de Barras]
```
- **Inicialização (`initAudioVisualizer(stream)`):**
  - Cria `audioCtx = new (window.AudioContext || window.webkitAudioContext)()`.
  - Cria `analyser = audioCtx.createAnalyser()`, configurado com `fftSize = 64` (32 faixas de frequência).
  - Conecta `source = audioCtx.createMediaStreamSource(stream)` a `analyser`.
- **Loop de Animação (`drawAudioVisualizer()`):**
  - Lê `analyser.getByteFrequencyData(dataArray)`.
  - Limpa o canvas e renderiza barras verticais proporcionais à amplitude, com bordas arredondadas e cores gradientes.
- **Encerramento (`stopAudioVisualizer()`):**
  - Executa `cancelAnimationFrame(visualizerAnimId)`.
  - Desconecta os nós e executa `audioCtx.close()` ou `suspend()`.
  - Limpa visualmente o canvas.
  - Resiliente: se a Web Audio API falhar ou for bloqueada por políticas do navegador, o erro é capturado e a gravação de áudio segue funcionando normalmente.

### 3.2 Gerenciador de Histórico (`HistoryManager`)
Funções em JavaScript puro no frontend:
- `loadHistory()`: Lê e faz parse do JSON em `localStorage.getItem("parakeet_transcription_history") || "[]"`.
- `saveHistory(items)`: Escreve no `localStorage` garantindo o limite de 50 itens (`items.slice(0, 50)`).
- `addHistoryEntry(text)`: Gera ID único (`Date.now().toString()`), timestamp ISO, adiciona no início da lista, salva e invoca `renderHistory()`.
- `deleteHistoryEntry(id)`: Filtra os itens removendo o ID correspondente e re-renderiza.
- `clearAllHistory()`: Pede confirmação e esvazia o histórico.
- `copyHistoryText(id)`: Localiza o texto pelo ID e copia via `navigator.clipboard.writeText`.
- `insertHistoryText(id)`: Localiza o texto e anexa ao `outputEl.value`.
- `renderHistory()`: Constrói dinamicamente os elementos DOM dos cards ou mensagem de vazio, atualizando o contador do cabeçalho.

---

## 4. Tratamento de Erros e Casos de Borda

1. **Microfone Bloqueado / Falha no AudioContext:**
   - Se `getUserMedia` ou `AudioContext` lançar exceção, o sistema captura, notifica no banner de status e não quebra a interface.
2. **Quota Excedida ou Falha no `localStorage`:**
   - Em caso de navegação anônima com `localStorage` desabilitado ou erro de cota, as operações de leitura e escrita tratam com `try/catch` e informam aviso sutil sem impedir o uso do ditado principal.
3. **Texto Vazio:**
   - Áudios que não contiverem fala detectada ou transcrição vazia não geram registros no histórico.
4. **HTML Injection / Sanitização:**
   - Textos inseridos nos cards de histórico utilizam `textContent` (ou sanitização estrita) para evitar qualquer problema de XSS com caracteres especiais.

---

## 5. Estratégia de Verificação e Testes

1. **Testes Automatizados do Servidor:**
   - Garantir que o servidor FastAPI continue servindo o `index.html` atualizado com código HTTP 200 via `tests/test_server.py`.
2. **Testes de Integração e Interface:**
   - Teste de sintaxe e parsing do HTML/JS via Node ou script de validação de DOM.
   - Validação da persistência de dados em `localStorage` (fluxo de salvar, ler, limitar a 50 itens e excluir).
   - Validação de desmontagem correta de nós de áudio e cancelamento de frames.
