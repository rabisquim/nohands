# 🎙️ Ditador por Voz — Local com Parakeet V3

Transcrição de áudio em texto **100% local**, sem API externa, sem custo por uso.
Modelo: [`nvidia/parakeet-tdt-0.6b-v3`](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) — multilíngue (25 idiomas europeus, incluindo **Português**), estado-da-arte em open-source ASR.

> Antes você usava **Groq (Whisper-large-v3)**. Agora tudo roda na sua máquina via FastAPI + ONNX Runtime.

---

## 📁 Estrutura

```
parakeet-ditado/
├── server.py          # Backend FastAPI que carrega o Parakeet V3
├── index.html         # Frontend (browser) — fala com o backend
├── requirements.txt
├── start.sh           # Script de start (cria venv, instala deps, sobe servidor)
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

A primeira execução:
1. Cria `.venv/`
2. Instala `fastapi`, `uvicorn`, `onnx-asr`, `onnxruntime` (~250 MB total)
3. Baixa o modelo Parakeet V3 do HuggingFace (~600 MB int8 / ~1.2 GB full)
4. Sobe o servidor em `http://127.0.0.1:8765`

Nas próximas vezes é instantâneo (modelo fica em cache).

### Abrir o frontend
O `index.html` precisa ser servido via HTTP (não pode ser `file://`):

```bash
# em outro terminal, dentro da pasta parakeet-ditado:
python3 -m http.server 8080
```

Abra **http://localhost:8080/index.html** no navegador. O status deve mostrar
`✅ Servidor online • modelo nvidia/parakeet-tdt-0.6b-v3 (int8)`.

> Dica: se o backend estiver em outra máquina/porta, edite o campo de URL na
> própria página (ele salva em `localStorage`).

---

## 🎯 Como usar

| Ação | Como |
|------|------|
| Gravar voz | Clique em **🎙️ Iniciar Gravação** ou `Ctrl+Shift+Espaço` |
| Transcrever arquivo | Clique em **📁 Transcrever arquivo de áudio** (mp3, m4a, ogg, wav, webm…) |
| Copiar texto | **📋 Copiar** |
| Baixar .txt | **💾 Baixar .txt** |
| Limpar | **🗑️ Limpar** |

O modelo Parakeet V3 já devolve **pontuação e capitalização automáticas**, então
o texto sai pronto pra colar em qualquer lugar.

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

1. **Transcrição parcial durante a gravação** (efeito "streaming" mandando chunks
   a cada 2–3s) — ótimo pra ditado longo.
2. **Timestamps por palavra** — Parakeet V3 devolve com `model.with_timestamps()`.
3. **Endpoint de upload maior** quebrando áudio em janelas com VAD
   (`model.with_vad(vad_model)`) — útil pra arquivos > 30s.
4. **Auto-detecção de idioma** — Parakeet V3 já detecta entre os 25 europeus
   automaticamente; basta remover qualquer forçagem de language.
5. **Hotword / comandos de voz** — combinação com um modelo leve tipo
   `whisper-tiny` rodando em paralelo.

É só me chamar que eu implemento qualquer dessas. 🤙

---

## ❓ Troubleshooting

**"❌ Servidor offline"** — o backend não está rodando. Rode `./start.sh` em um terminal.

**"ffmpeg não encontrado"** — instale conforme a seção *Instalação*.

**Modelo baixando muito lento** — primeira execução só. Depois fica cacheado em
`~/.cache/huggingface/hub/`.

**Transcrição vazia pra áudio de música/cantar** — o Parakeet v3 transcreve
fala, não letras de música. Esse recurso é só da versão TDT 0.6B v2 (inglês).

**Erros `CUDAExecutionProvider` no Windows** — normalmente é falta de
`onnxruntime-gpu` + CUDA 12.x. Use `USE_GPU=0` para forçar CPU.
