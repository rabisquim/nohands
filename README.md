# 🎙️ Ditador por Voz (nohands) — Local com Parakeet V3

Transcrição de áudio em texto **100% local e privada**, sem API externa, sem telemetria e sem custo por uso.
Alimentado pelo modelo [`nvidia/parakeet-tdt-0.6b-v3`](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) — estado-da-arte em ASR open-source multilíngue (25 idiomas europeus, incluindo **Português do Brasil**), executado via FastAPI e ONNX Runtime.

Interface moderna **Studio Pro Dark** com design refinado, feedback tátil em tempo real e **100% offline** (zero dependências de CDNs).

---

## ✨ Interface Studio Pro

A interface web foi desenhada com estética inspirada em softwares de áudio profissionais e ferramentas modernas (*Linear Dark*):

- **🎨 Design System Dark Refinado:** Paleta profunda (`#07090e`, `#0e1322`), micro-interações táteis, realces em neon ciano/esmeralda e tipografia limpa.
- **🎙️ Hero Recording Button:** Botão central em formato de pílula pro com efeito de pulso luminoso e feedback dinâmico de estado ("Gravando...").
- **📊 VU Meter Neon em Tempo Real:** Visualizador de espectro sonoro com barras neon dinâmicas via Web Audio API indicando a captação do microfone.
- **⌨️ Atalho Global:** Inicie ou pare a gravação instantaneamente com o atalho `<kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>Espaço</kbd>`.
- **📝 Card do Editor Pro:** Área de texto unificada com anel de foco luminoso (`focus-within`) e toolbar integrada com ícones vetoriais SVG inline.
- **🔢 Contador em Tempo Real:** Indicador dinâmico de palavras e caracteres (`X palavras • Y caracteres`) atualizado ao digitar, transcrever ou carregar do histórico.
- **⏳ Timeline de Histórico:** Linha do tempo vertical elegante com as últimas 50 transcrições salvas localmente no navegador (ações: Copiar, Inserir no editor, Excluir item ou Limpar Tudo), com proteção contra XSS.
- **🔔 Notificações Toast:** Sistema não-intrusivo de toasts flutuantes para confirmações de cópia, erros e alertas.
- **⚙️ Popover de Conexão Discreto:** Status do backend em pílula no topo (`🟢 Parakeet V3 Ready`), com popover flutuante para configuração de URL sem poluir o layout.
- **🔒 100% Offline & Seguro:** Sem CDNs externas, fontes remotas ou scripts de terceiros. Funciona mesmo sem conexão com a internet.

---

## 📁 Estrutura

```
parakeet-ditado/
├── server.py          # Backend FastAPI (carrega o Parakeet V3 e serve a UI)
├── frontend/          # Interface web estática Studio Pro
│   └── index.html     # Frontend unificado (HTML, CSS e JS puros, zero CDN)
├── tests/             # Suíte de testes automatizados (backend e frontend)
│   ├── test_server.py
│   └── test_frontend.py
├── requirements.txt
├── start.sh           # Script de start unificado (sobe servidor e abre navegador)
└── README.md
```

---

## ⚙️ Instalação (uma vez)

### 1. Dependências do sistema
- **Python 3.10+**
- **ffmpeg** (usado para converter o áudio do navegador em wav 16 kHz mono)
  - Linux: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Windows: [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) — coloque `ffmpeg.exe` no PATH

### 2. (Opcional) GPU NVIDIA
Se você tem placa NVIDIA e quer inferência 10–50× mais rápida, instale o CUDA Toolkit
(12.x) e troque o `onnx-asr[cpu,hub]` por uma versão com suporte a GPU:

```bash
pip uninstall onnxruntime -y
pip install onnxruntime-gpu
```

O `server.py` detecta automaticamente: se `CUDAExecutionProvider` estiver disponível,
usa GPU; senão cai pra CPU.

---

## ▶️ Como rodar

```bash
cd parakeet-ditado
chmod +x start.sh
./start.sh
```

O comando único `./start.sh`:
1. Cria o `.venv/` e instala as dependências (se necessário)
2. Sobe o servidor FastAPI unificado (backend e frontend) em `http://127.0.0.1:8765`
3. Abre automaticamente a interface no navegador (se houver interface gráfica disponível)

> Caso esteja rodando sem interface gráfica ou em uma máquina remota, basta abrir **http://127.0.0.1:8765** no navegador. O status no topo deve mostrar `🟢 Parakeet V3 Ready`.

A primeira execução baixa o modelo Parakeet V3 do HuggingFace (~600 MB int8 / ~1.2 GB full). Nas próximas vezes a inicialização é instantânea (modelo fica em cache).

> Dica: se o backend estiver em outra máquina ou porta, clique no ícone de engrenagem na pílula de status no topo para editar a URL (ela fica salva no `localStorage`).

---

## 🎯 Como usar

| Ação | Como |
|------|------|
| **Gravar voz** | Clique no botão **Iniciar Ditado** ou pressione `Ctrl+Shift+Espaço` |
| **Visualizador de áudio (VU Meter)** | Barras neon dinâmicas oscilam em tempo real durante a gravação indicando a captação do microfone |
| **Transcrever arquivo** | Clique em **Subir Áudio** na toolbar do editor (suporta mp3, m4a, ogg, wav, webm…) |
| **Copiar texto** | Clique em **Copiar** na toolbar (feedback visual via Toast) |
| **Baixar transcrição** | Clique em **Baixar .txt** para salvar o texto localmente com timestamp |
| **Limpar editor** | Clique em **Limpar** para zerar a área de texto |
| **Histórico em Timeline** | Feed visual abaixo do editor com as últimas 50 transcrições salvas localmente no navegador (ações: Copiar, Inserir no editor, Excluir item ou Limpar Tudo) |
| **Configurações de Conexão** | Clique na pílula de status no topo direito para abrir o popover e ajustar ou testar a URL da API |

O modelo Parakeet V3 já devolve **pontuação e capitalização automáticas**, então o texto sai pronto pra colar em qualquer lugar.

---

## 🧪 Testes Automatizados

O projeto conta com suíte de testes unitários para o backend e integridade estrutural do frontend:

```bash
# Executar todos os testes
.venv/bin/python -m unittest discover tests

# Ou individualmente:
.venv/bin/python -m unittest tests/test_server.py
.venv/bin/python -m unittest tests/test_frontend.py
```

---

## 🔧 Variáveis de ambiente

| Var | Default | O que faz |
|---|---|---|
| `HOST` | `127.0.0.1` | Interface onde o servidor escuta |
| `PORT` | `8765` | Porta do servidor |
| `PARAKEET_MODEL` | `nemo-parakeet-tdt-0.6b-v3` | Modelo do `onnx-asr` (ver lista abaixo) |
| `PARAKEET_QUANT` | `int8` | `int8` (CPU) / `fp16` (GPU) / `None` (full) |
| `USE_GPU` | `auto` | `0` força CPU, `1` força GPU |

### Modelos alternativos suportados pelo `onnx-asr`
- `nemo-parakeet-tdt-0.6b-v3` ← **recomendado** (multilíngue, 25 idiomas)
- `nemo-parakeet-tdt-0.6b-v2` (inglês, um pouco mais rápido)
- `nemo-parakeet-ctc-0.6b` (inglês, CTC puro)
- `nemo-parakeet-rnnt-0.6b` (inglês, RNN-T)

Exemplo: usar v2 inglês full precision:
```bash
PARAKEET_MODEL=nemo-parakeet-tdt-0.6b-v2 PARAKEET_QUANT= python server.py
```

---

## 🚀 Próximos passos (sugestões de evolução)

Funcionalidades fáceis de adicionar por cima desta base:

1. **Transcrição parcial durante a gravação** (efeito "streaming" mandando chunks a cada 2–3s) — ótimo pra ditado longo.
2. **Timestamps por palavra** — Parakeet V3 devolve com `model.with_timestamps()`.
3. **Endpoint de upload maior** quebrando áudio em janelas com VAD (`model.with_vad(vad_model)`) — útil pra arquivos > 30s.
4. **Auto-detecção de idioma** — Parakeet V3 já detecta entre os 25 europeus automaticamente; basta remover qualquer forçagem de language.
5. **Hotword / comandos de voz** — combinação com um modelo leve tipo `whisper-tiny` rodando em paralelo.

---

## ❓ Troubleshooting

**"❌ Servidor offline"** — o backend não está rodando. Rode `./start.sh` em um terminal ou verifique se a porta `8765` está livre.

**"ffmpeg não encontrado"** — instale conforme a seção *Instalação*.

**Modelo baixando muito lento** — primeira execução só. Depois fica cacheado em `~/.cache/huggingface/hub/`.

**Transcrição vazia pra áudio de música/cantar** — o Parakeet v3 transcreve fala, não letras de música. Esse recurso é só da versão TDT 0.6B v2 (inglês).

**Erros `CUDAExecutionProvider` no Windows** — normalmente é falta de `onnxruntime-gpu` + CUDA 12.x. Use `USE_GPU=0` para forçar CPU.
