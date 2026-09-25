# Design Spec: Redesign Visual Studio Pro (Adeus "IA Slop")

- **Data**: 2026-09-25
- **Status**: Aprovado para Implementação
- **Autor**: Robson Paulo / Pair Programming com Antigravity

---

## 1. Visão Geral e Objetivos

O projeto **nohands** possui todas as funcionalidades de backend e lógica de interface funcionando perfeitamente (gravação, envio ao Parakeet V3, VU meter e histórico local). No entanto, a interface atual sofre da estética genérica e descuidada de protótipos de IA ("IA Slop"):
- Caixa cinza única centralizada sem refinamento visual.
- Input de URL e botão de teste de servidor poluindo permanentemente o topo da tela.
- Sobrecarga de emojis soltos no lugar de ícones vetoriais.
- Falta de hierarquia visual, espaçamento harmônico e micro-interações táteis.

O objetivo deste redesign é elevar a aplicação para o padrão visual **Studio Pro / Linear Dark**, entregando uma ferramenta com acabamento profissional, agradável e moderno, mantendo **100% de compatibilidade offline e zero dependências externas**.

---

## 2. Requisitos e Restrições

### 2.1 Requisitos de Design e UX
- **RF01 - Design System Studio Pro:**
  - Paleta escura profunda com camadas de elevação:
    - Fundo da página: `--bg: #07090e`
    - Superfície dos cards: `--surface: #0e1322`
    - Superfície elevada / hover: `--surface-hover: #161f36`
    - Bordas sutis: `--border: rgba(255, 255, 255, 0.08)`
    - Acentos neon: Ciano (`--cyan: #38bdf8`), Azul (`--blue: #3b82f6`), Esmeralda (`--emerald: #10b981`), Vermelho gravação (`--rec: #ef4444`).
  - Tipografia limpa com espaçamento moderno e proporção áurea de hierarquia.
  - Ícones SVG inline minimalistas (estilo Lucide/Heroicons) substituindo todos os emojis.
- **RF02 - Topbar & Status Popover:**
  - Logo minimalista com glifo de onda sonora + `nohands`.
  - Pílula de status no canto superior direito (`🟢 Parakeet V3 Ready`).
  - Ao clicar na pílula de status, abre um popover/modal flutuante discreto com as configurações de conexão (`#serverUrl`, `#checkBtn`, `#serverDot`), mantendo os IDs compatíveis para testes.
- **RF03 - Hero de Gravação & VU Meter:**
  - Botão principal (`#recordBtn`) em formato de pílula pro (`border-radius: 9999px`), ícone SVG de microfone e efeito de pulso luminoso enquanto grava.
  - Badge de atalho abaixo com visual de teclas físicas `<kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>Espaço</kbd>`.
  - VU meter (`#vuContainer` e canvas `#vuMeter`) redesenhado com iluminação neon esmeralda-ciano e transição suave de expansão.
- **RF04 - Editor de Texto com Toolbar Integrada & Contador:**
  - Card integrado unindo a área de texto (`#output`) e a toolbar de ações rápidas.
  - Toolbar com botões vetoriais: 📋 Copiar, 💾 Baixar .txt, 📁 Subir Áudio e 🗑️ Limpar.
  - Contador em tempo real no rodapé do editor: `X palavras • Y caracteres`.
- **RF05 - Sistema de Toasts Flutuantes:**
  - Substituir alertas intrusivos por notificações discretas no canto inferior da tela (`#toastContainer`).
  - Deslizam suavemente e somem após 3 segundos.
- **RF06 - Timeline de Histórico:**
  - Histórico apresentado em formato de feed/timeline elegante (`#historySection`, `#historyList`, `#historyCount`, `#clearHistoryBtn`).
  - Cards com cantos arredondados, timestamp formatado seguro contra XSS (`textContent`) e botões rápidos com ícones.

### 2.2 Requisitos de Compatibilidade e Preservação
- **Zero Dependências Externas:** Proibido o uso de CDNs (sem Tailwind CDN, FontAwesome ou bibliotecas externas). Todos os estilos e SVGs devem ser nativos e inline no arquivo.
- **Preservação de IDs e Contratos:** Todos os elementos e IDs testados pela suíte automatizada (`tests/test_frontend.py` e `tests/test_server.py`) devem ser estritamente preservados:
  - `#vuContainer`, `#vuMeter`, `initAudioVisualizer`, `stopAudioVisualizer`
  - `#historySection`, `#historyList`, `#historyCount`, `addHistoryEntry`, `deleteHistoryEntry`, `clearAllHistory`
  - Chave de storage `parakeet_transcription_history` e limite FIFO de 50 itens.
  - `#serverUrl`, `#serverDot`, `#checkBtn`, `#status`, `#output`, `#recordBtn`, `#fileInput`.

---

## 3. Arquitetura de Componentes da Interface

```
┌────────────────────────────────────────────────────────────────────────┐
│  [🎙️] nohands                                   [ 🟢 Parakeet V3 Ready ⚙️ ]│ Topbar
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│                      ┌───────────────────────┐                         │
│                      │  (🎙️) Iniciar Ditado  │                         │ Hero
│                      └───────────────────────┘                         │
│                       [ Ctrl + Shift + Espaço ]                        │
│                                                                        │
│              ┌─ [VU Meter Neon] ─────────────────────┐                 │
│              │   ▂ ▃ ▅ ▆ █ ▇ ▅ ▃ ▂                   │                 │
│              └───────────────────────────────────────┘                 │
│                                                                        │
│  ┌─ [Card do Editor Pro] ───────────────────────────────────────────┐  │
│  │                                                                  │  │ Editor
│  │  Área de transcrição e digitação com tipografia refinada...      │  │
│  │                                                                  │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │  [Copiar]  [Baixar .txt]  [Subir Áudio]  [Limpar]   0 p. • 0 c.  │  │ Toolbar
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  ▼ Histórico de Transcrições (3)                      [ Limpar Tudo ]  │ Timeline
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  🕒 25/09 às 13:40                                               │  │
│  │  "Texto transcrito com precisão..."                              │  │
│  │  [Copiar]  [Inserir]  [Excluir]                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Estratégia de Verificação e Testes

1. **Testes Unitários de Frontend:**
   - Executar `.venv/bin/python -m unittest tests/test_frontend.py` e garantir 100% de aprovação.
2. **Testes Unitários do Servidor:**
   - Executar `.venv/bin/python -m unittest tests/test_server.py` confirmando que a rota `/` e `/health` continuam íntegras.
3. **Validação de Responsividade e Micro-Interações:**
   - Layout fluido em desktop e mobile (responsivo via flexbox e max-width).
   - Teste do contador de palavras/caracteres.
   - Teste dos Toasts flutuantes.
   - Teste da alternância do popover de conexão.
