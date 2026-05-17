# Catatan Analisis Refactoring — RJ Auto Metadata

> **Status**: Catatan diskusi. Belum ada implementasi. UI refactor belum dibahas (nanti di pesan selanjutnya).

---

## 1. Item #1 — Refactor ke OpenAI Endpoint (Tinggalkan REST Native)

### Situasi Saat Ini

| Provider | Endpoint | Format |
|---|---|---|
| **Gemini** | `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent` | **Native REST Gemini** (non-standard) |
| **OpenAI** | `https://api.openai.com/v1/responses` | OpenAI **Responses API** (bukan Chat Completions!) |
| **OpenRouter** | `https://openrouter.ai/api/v1/chat/completions` | OpenAI Chat Completions ✅ |
| **Groq** | `https://api.groq.com/openai/v1/chat/completions` | OpenAI Chat Completions ✅ |
| **KoboiLLM** | `https://litellm.koboi2026.biz.id/chat/completions` | OpenAI Chat Completions ✅ |

### Temuan Kritis

**Gemini** adalah satu-satunya yang pakai native REST. Berdasarkan Auto Clipper (`config.py`):
```python
"Gemini": {
    "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
}
```
Gemini **sudah punya OpenAI-compatible endpoint** (`v1beta/openai/`) yang bisa dipakai langsung dengan OpenAI SDK. Format request/response identik dengan Chat Completions standard.

**OpenAI** saat ini pakai **Responses API** (`/v1/responses`) — ini endpoint baru yang lebih powerful tapi berbeda dari Chat Completions. Response struktur-nya: `output[].content[].text` bukan `choices[0].message.content`. Ini yang bikin `_parse_openai_response` punya logic parsing yang berbeda dan lebih kompleks.

### Dampak Refactor

| Komponen | Perubahan | Besar? |
|---|---|---|
| `gemini_api.py` | Ganti endpoint + payload ke OpenAI compat → **hapus ~500 baris** logic SDK/REST hybrid | **Besar** |
| `openai_api.py` | Ganti dari Responses API → Chat Completions (`/v1/chat/completions`) | **Sedang** |
| `gemini_api.py` | Hapus `_attempt_gemini_sdk_request`, `_attempt_gemini_rest_request`, model rotation logic | **Besar** |
| Parser | Semua provider jadi format sama `choices[0].message.content` | Simplifikasi |

### Jawaban: Apakah Pengaruhnya Besar?
> **YA, untuk Gemini — SANGAT BESAR.** Ini bukan sekadar ganti URL. Ini berarti:
> - Hapus seluruh SDK path (`google.genai` SDK)
> - Hapus seluruh native REST path dengan binary image
> - Ganti ke OpenAI SDK (`from openai import OpenAI`) dengan `base_url` Gemini compat
> - Format payload jadi standard: `messages`, `image_url`, `response_format: json_object`
> - Thinking parts tidak lagi jadi masalah karena Gemini compat endpoint tidak expose raw thinking structure
> - Response parsing jadi sama persis dengan Groq/OpenRouter/KoboiLLM
>
> **Untuk OpenAI:** Sedang. Ganti dari Responses API ke Chat Completions juga simplifikasi parser besar (dari `output[]` ke `choices[]`). Tapi perlu verifikasi apakah ada fitur spesifik Responses API yang dibutuhkan.
>
> **Benefit besar**: Setelah refactor, semua 5 provider punya pola yang identik — satu `_parse_response` bisa dipakai semua.

---

## 2. Item #2 — Hapus Hardcoded Model, Auto-Save ke Config JSON

### Apa yang Hardcoded Saat Ini

```
gemini_api.py    → GEMINI_MODELS = [...7 model...]       DEFAULT_MODEL = "gemini-2.0-flash"
groq_api.py      → GROQ_MODEL_PRESETS = {Scout, Maverick}  DEFAULT_MODEL = "Llama 4 Maverick" (DEAD)
openai_api.py    → OPENAI_MODEL_PRESETS = {...10 model...}  DEFAULT_MODEL = "gpt-5"
openrouter_api.py → OPENROUTER_MODEL_PRESETS = {...16 model...} DEFAULT_MODEL = "openai/gpt-5"
koboillm_api.py  → KOBOILLM_MODEL_PRESETS = {...10 model...}  DEFAULT_MODEL = "gemini/gemini-2.5-flash"
```

**Total**: ~50+ model IDs hardcoded di kode, tersebar di 5 file berbeda.

### Yang Diinginkan
- Model tidak di-hardcode di kode Python
- Disimpan di config JSON (sama seperti Auto Clipper menyimpan `models_per_provider`)
- Kalau model belum ada di config, fallback ke default minimum yang valid

### Catatan Teknis
Config manager RJ Metadata saat ini ada di `src/config/` (belum dibaca detail). Perlu cek apakah ada JSON config yang sudah ada atau perlu dibuat baru.

---

## 3. Item #3 & #4 — Dynamic Model Fetch + Custom Provider

### Pattern dari Auto Clipper (Referensi)

```python
# settings_view.py — _fetch_models_async()
from openai import OpenAI
client = OpenAI(api_key=api_key, base_url=base_url, timeout=10.0)
result = client.models.list()  # GET /v1/models
models = sorted(m.id for m in result.data)
```

`GET /v1/models` tersedia di:
| Provider | Endpoint | Support |
|---|---|---|
| Groq | `https://api.groq.com/openai/v1/models` | ✅ Standard |
| OpenRouter | `https://openrouter.ai/api/v1/models` | ✅ Standard |
| KoboiLLM | `https://litellm.koboi2026.biz.id/models` | ✅ LiteLLM standard |
| Gemini (compat) | `https://generativelanguage.googleapis.com/v1beta/openai/models` | ✅ (via compat endpoint) |
| OpenAI | `https://api.openai.com/v1/models` | ✅ Standard |

### Pertanyaan User: Bisa Filter Vision-Only Models?

**Bisa! Ada 3 pendekatan:**

**Pendekatan A — Filter dari response `/v1/models` (paling bersih):**
OpenRouter response `/v1/models` menyertakan field `architecture.input_modalities`:
```json
{
  "id": "google/gemini-2.5-flash",
  "architecture": {
    "input_modalities": ["file", "image", "text"],  ← filter ini
    "output_modalities": ["text"]
  }
}
```
Bisa filter: `"image" in model.architecture.input_modalities`

**Pendekatan B — Whitelist pattern matching (lebih sederhana):**
Setelah fetch semua models, filter berdasarkan string patterns yang diketahui vision-capable:
```python
VISION_PATTERNS = ["llama-4", "gpt-4", "gpt-5", "gemini", "claude-3", "claude-sonnet", "mistral-pixtral", "qwen-vl"]
vision_models = [m for m in all_models if any(p in m.lower() for p in VISION_PATTERNS)]
```

**Pendekatan C — Hybrid (fetch + OpenRouter metadata):**
Khusus OpenRouter, bisa pakai `GET /api/v1/models?supported_parameters=tools` atau filter dari `input_modalities`.

**Rekomendasi**: Pendekatan A untuk OpenRouter (punya metadata), Pendekatan B untuk provider lain (Groq, OpenAI tidak expose modalities di `/v1/models`). Di Groq, semua non-vision model tidak menerima image input dan akan return error — bisa detect dari error response juga.

### Custom Provider
Seperti Auto Clipper's `"Custom"` provider: user isi sendiri `base_url` dan API key, lalu fetch models dari `/v1/models`. Butuh field tambahan di UI dan config JSON.

---

## 4. Item #5 — Hapus Code Redundant / Dead Code

### Temuan Spesifik

#### `gemini_api.py` (~770 baris) — SANGAT BLOATED
```python
# Dead/redundant setelah refactor ke OpenAI compat:
- _attempt_gemini_sdk_request()     # ~170 baris — seluruh SDK path
- _attempt_gemini_rest_request()    # ~175 baris — seluruh native REST path  
- _attempt_gemini_request()         # dispatcher, tidak perlu lagi
- get_sdk_client()                  # tidak perlu lagi
- should_use_sdk()                  # tidak perlu lagi
- GENAI_SDK_AVAILABLE               # tidak perlu lagi
- get_thinking_budget_for_model()   # tidak perlu lagi (ditangani compat endpoint)
- get_thinking_level_for_model()    # tidak perlu lagi
- get_thinking_config_for_model()   # tidak perlu lagi
- is_gemini_3_model()               # tidak perlu lagi
- MODEL_LAST_USED, MODEL_LOCK       # tidak perlu lagi (auto rotation dihapus)
- select_next_model()               # tidak perlu lagi
- wait_for_model_cooldown()         # tidak perlu lagi
- select_best_fallback_model()      # tidak perlu lagi
- calculate_smart_delay()           # tidak dipakai
- DEBUG_FORCE_FAILURE               # debug artifact
```
Estimasi: dari ~770 baris → **~150-200 baris** setelah refactor.

#### `openai_api.py` (~686 baris) — Redundant parsers
```python
# Setelah pindah ke Chat Completions, tidak perlu lagi:
- _parse_openai_response()         # logic kompleks untuk Responses API format
- _extract_metadata_from_text_fallback()  # bisa di-shared dengan provider lain
- _JSON_SCHEMA usage via "text.format"   # Responses API specific
- _STRUCTURED_OUTPUT_MODEL_PREFIXES    # bisa disederhanakan
```

#### `openrouter_api.py` & `koboillm_api.py` — Duplikasi identik
Kedua file ini hampir identik strukturnya. `_clean_json_text()` **diduplikasi persis** di:
- `openrouter_api.py` L33-46
- `koboillm_api.py` L33-46
- `openai_api.py` L32-45

→ Bisa dipindah ke `src/utils/json_utils.py` sebagai shared utility.

#### `provider_manager.py` — if-else chain bisa disederhanakan
```python
# L179-255: if-elif chain panjang per provider
if provider_key == PROVIDER_GEMINI:
    result = module.get_gemini_metadata(...)
elif provider_key == PROVIDER_OPENROUTER:
    result = module.get_openrouter_metadata(...)
# dll...
```
→ Seharusnya `module.get_metadata(...)` dengan interface yang seragam.

#### `openai_api.py` L119-128 — Duplikasi di `_STRUCTURED_OUTPUT_MODEL_PREFIXES`
```python
_STRUCTURED_OUTPUT_MODEL_PREFIXES: Tuple[str, ...] = (
    "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano",
    "gpt-4o", "gpt-4o-mini",
    "gpt-4o",   # ← DUPLIKASI (gpt-4o muncul 2x)
    "gpt-5", "gpt-5-mini", "gpt-5-nano",
)
```

#### Commented-out code yang tidak perlu
Di beberapa file ada kode yang di-comment out dan tidak perlu:
```python
# try:
#     log_message(f"[Groq] Raw keywords: {len(raw_keywords)}...", "debug")
# except Exception:
#     pass
```
Ada di `groq_api.py` L206-209, `openrouter_api.py` L399-402, `openai_api.py` L336-339.

---

## 5. Item #6 — Terminal Log Fix

Detail sudah ada di `implementation_plan.md`.

**Rangkuman**: `logging.py` perlu `_TERMINAL_PRINT_TAGS = {"warning", "error", "critical", "success"}` filter sebelum `print()`.

---

## 6. Perbandingan Git & Dokumentasi

### RJ Auto Metadata — State Saat Ini ❌

**Branch**: Hanya `main` (satu branch, tidak ada `dev`, tidak ada task branches)
```
* main
  remotes/origin/HEAD -> origin/main
  remotes/origin/main
```

**Commit style**: Campuran — ada yang conventional (`feat:`, `fix:`, `docs:`, `chore:`), ada yang tidak. Tapi semua di `main` langsung.

**Commit history masalah**:
```
499c47f feat: add Gemini 3.x model support and fix API request handling - [panjang banget]
1cf278c feat: Add JSON cleaning function and update model configurations across APIs - [masih panjang]
```
→ Commit messages terlalu verbose di body, tapi single-line di graph. Pola tidak konsisten.

**Dokumentasi**:
- ✅ `README.md` (28KB — lumayan lengkap)
- ✅ `CHANGELOG.md` (43KB — ada, tapi jadi satu-satunya sumber kebenaran)
- ✅ `CONTRIBUTING.md` (1KB — ada tapi sangat minimal)
- ✅ `QUICK_START_GUIDE.md`
- ❌ **Tidak ada `docs/` folder**
- ❌ **Tidak ada `AGENTS.md`** (tidak ada instruksi untuk AI agent)
- ❌ **Tidak ada `GIT_POLICY.md`**
- ❌ **Tidak ada `ARCHITECTURE.md`**
- ❌ **Tidak ada task/phase tracking**
- ❌ **Tidak ada agent logs**

**Masalah lain**: Ada file `logs` di root (harusnya di `.gitignore`), ada `api_jikaperlu/` dengan API keys di repo (!!!).

---

### RJ Auto Clipper — State ⚠️

**Branch**: Semua di `main`, tapi punya versioning yang lebih baik (v1.0.0 → v1.1.2).

**Commit style**: Lebih rapi, messages lebih ringkas.

**Dokumentasi**:
- ✅ `README.md`, `CHANGELOG.md`
- ❌ Tidak ada `docs/` folder
- ❌ Tidak ada `AGENTS.md`
- ❌ Tidak ada task branches

---

### RJ Music Studio — Best Practice ✅✅✅

**Branch structure**:
```
main          ← release baseline only
dev           ← integration branch
task/phase-*  ← 35+ task branches, semua terpisah
```

**Commit style**: Sangat konsisten conventional commits. Setiap perubahan ada konteksnya.

**Dokumentasi (docs/ folder — 22 files)**:
```
AGENTS.md            ← instruksi AI agent
ARCHITECTURE.md      ← desain sistem
CURRENT_STATE.md     ← state terkini
HANDOFF.md           ← handoff antar sesi
DECISIONS.md         ← keputusan arsitektur
GIT_POLICY.md        ← aturan git
DEVELOPMENT_WORKFLOW.md
ROADMAP.md
SECURITY.md
agent-logs/          ← log aktivitas agent per sesi
```

**Key features dari AGENTS.md Music Studio yang tidak ada di Metadata**:
1. Required reading order sebelum edit
2. Phase boundary rules
3. Explicit verification commands
4. Security-first rules
5. Agent role workflow (Planner, Architect, Implementer, etc.)

---

### Perbandingan Tabel

| Aspek | RJ Auto Metadata | RJ Auto Clipper | RJ Music Studio |
|---|---|---|---|
| Branch strategy | Main only ❌ | Main only ❌ | Main + dev + task/* ✅ |
| Commit style | Tidak konsisten ⚠️ | Lebih rapi ✅ | Conventional commit ✅ |
| docs/ folder | ❌ | ❌ | ✅ (22 files) |
| AGENTS.md | ❌ | ❌ | ✅ |
| GIT_POLICY.md | ❌ | ❌ | ✅ |
| ARCHITECTURE.md | ❌ | ❌ | ✅ |
| Agent logs | ❌ | ❌ | ✅ |
| CHANGELOG | ✅ (lumayan) | ✅ | ada di HANDOFF |
| API keys di repo | ⚠️ `api_jikaperlu/` | ❌ | ❌ |

---

## 7. Endpoint Reference (setelah refactor ke OpenAI compat)

| Provider | Base URL | Model Fetch | Notes |
|---|---|---|---|
| Gemini | `https://generativelanguage.googleapis.com/v1beta/openai/` | `GET /models` | OpenAI compat |
| OpenAI | `https://api.openai.com/v1` | `GET /models` | Standard |
| OpenRouter | `https://openrouter.ai/api/v1` | `GET /models` | Returns `input_modalities` |
| Groq | `https://api.groq.com/openai/v1` | `GET /models` | Standard OpenAI compat |
| KoboiLLM | `https://litellm.koboi2026.biz.id` | `GET /models` | LiteLLM proxy |
| Custom | (user-defined) | `GET /models` | OpenAI compat assumed |

---

## 8. Keputusan yang Sudah Diambil (Open Questions → Resolved)

| Q | Keputusan |
|---|---|
| **Q1 — OpenAI endpoint** | Tetap pakai **Responses API** (`/v1/responses`) untuk OpenAI. Provider lain pakai OpenAI Chat Completions compat. |
| **Q2 — Gemini Auto Rotation** | **Hapus Auto Rotation.** Model dipilih user dari hasil fetch dinamis. |
| **Q3 — Custom provider** | Field URL custom seperti Auto Clipper. Detail masuk scope UI refactor. |
| **Q4 — Vision filter** | **Tidak perlu filter.** Fetch semua model, tampilkan semua, user yang tentukan sendiri mana yang vision-capable. |
| **Q5 — `api_jikaperlu/` folder** | User akan hapus manual dari repo dan masuk `.gitignore`. |

---

## 9. UI Refactoring — Analisis Detail

> Berdasarkan screenshot (coretan user) + deep dive `src/ui/app.py` (1738 baris).

### Layout Saat Ini — "Settings and API Keys" Section

```
[col=0: API Textbox (height=60, 3 rows span)] | [col=1: api_buttons1] | [col=2: api_buttons2] | [col=3: process_buttons]
                                               |   [Check  ]           |   [Save   ]           |   [Start Processing]
                                               |   [Load   ]           |   [Delete ]           |   [Stop            ]
[api_paid_frame: Provider dropdown (colspan 1+2, sticky=sew)]         |                       |   [Clear Log        ]
```

### Target Layout Setelah Refactor

```
[col=0: API Key field (2 baris tinggi)] | [col=1: Check  ] [col=2: Fetch  ] | [col=3: Start Processing]
                                        | [col=1+2: Provider dropdown      ] | [Stop                   ]
[col=0: Custom URL field (1 baris)]     | [col=1+2: Model dropdown          ] | [Clear Log              ]
```

---

### Item #1 — Hapus Button Load & Delete

**UI Changes** (`_create_combined_api_settings_frame`, L382-392):
```python
# HAPUS semua ini:
self.load_api_button = ctk.CTkButton(..., text="Load", command=self._load_api_keys, ...)  # L385-386
self.delete_api_button = ctk.CTkButton(..., text="Delete", command=self._delete_selected_api_key, ...)  # L391-392
```

**Backend functions yang harus DIHAPUS total** (`app.py`):
- `_load_api_keys()` — L699-720 (~22 baris) — buka file dialog, baca .txt file
- `_save_api_keys()` — L722-744 (~23 baris) — buka save dialog, tulis .txt file  
- `_delete_selected_api_key()` — L746-813 (~68 baris) — delete key dari list berdasarkan cursor/selection

**Ripple effects** — referensi ke button yang harus dibersihkan:
| Lokasi | Baris | Kode | Aksi |
|---|---|---|---|
| `_disable_ui_during_processing()` | L1386-1388 | `self.load_api_button.configure(...)`, `self.save_api_button.configure(...)`, `self.delete_api_button.configure(...)` | **HAPUS** |
| `_reset_ui_after_processing()` | L1556-1558 | `self.load_api_button.configure(...)`, `self.save_api_button.configure(...)`, `self.delete_api_button.configure(...)` | **HAPUS** |

---

### Item #2 — Pindah Provider Dropdown ke Row Load/Delete (sejajar Stop)

**Saat ini** (L395-406): Provider dropdown ada di `api_paid_frame`, di-grid ke `row=1, column=1, columnspan=2, sticky="sew"` — yaitu menempel di bawah (south) bersama Check/Load.

**Target**: Provider dropdown pindah ke **row=1 col=1, colspan=2** yang sebelumnya ditempati Load+Delete, tapi now sejajar horizontal dengan **Stop** button (bukan Check).

```python
# SEBELUM: api_buttons1 + api_buttons2 masing-masing punya 2 button (Check+Load, Save+Delete)
# SESUDAH: 
# - api_buttons1: hanya [Check] saja
# - provider_dropdown: mengisi area col=1+2 di row tengah (sejajar Stop)
```

**Implikasi**: `api_buttons1` dan `api_buttons2` perlu di-reorganize. Load/Delete dihapus, jadi:
- `col=1`: hanya `Check` button
- `col=2`: hanya `Fetch` button (bekas `Save`)
- Provider dropdown: pindah ke baris kedua, `colspan=2` sejajar dengan Stop

---

### Item #3 — Save → Fetch Button

**UI Changes** (L388-389):
```python
# SEBELUM:
self.save_api_button = ctk.CTkButton(..., text="Save", command=self._save_api_keys, ...)
# SESUDAH:
self.fetch_models_button = ctk.CTkButton(..., text="Fetch", command=self._fetch_models, ...)
```

**Fungsi `_save_api_keys()` DIHAPUS total** (sudah di-cover di Item #1 di atas).

**Fungsi baru `_fetch_models()` ditambahkan**:
```python
def _fetch_models(self):
    """Fetch model list dari API endpoint provider yang dipilih."""
    api_keys = self._get_keys_from_textbox()
    if not api_keys:
        self._log("Enter API key first before fetching models.", "warning")
        return
    
    base_url = self.base_url_var.get().strip()  # dari field URL baru
    provider = self.provider_var.get()
    api_key = api_keys[0]  # pakai key pertama untuk fetch
    
    self.fetch_models_button.configure(state=tk.DISABLED, text="Fetching...")
    
    def _do_fetch():
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=base_url, timeout=10.0)
            result = client.models.list()
            models = sorted(m.id for m in result.data)
            self.after(0, lambda: self._on_models_fetched(models))
        except Exception as ex:
            self.after(0, lambda: self._on_models_fetch_error(str(ex)))
    
    threading.Thread(target=_do_fetch, daemon=True).start()

def _on_models_fetched(self, models):
    self.available_models = models
    if hasattr(self, 'model_dropdown'):
        self.model_dropdown.configure(values=models)
        if models:
            self.model_dropdown.set(models[0])
            self.model_var.set(models[0])
    self.fetch_models_button.configure(state=tk.NORMAL, text="Fetch")
    self._log(f"Fetched {len(models)} models from provider.", "success")

def _on_models_fetch_error(self, error_msg):
    self.fetch_models_button.configure(state=tk.NORMAL, text="Fetch")
    self._log(f"Failed to fetch models: {error_msg}", "error")
```

**Ripple di `_disable_ui_during_processing()` dan `_reset_ui_after_processing()`**:
- Ganti `self.save_api_button` → `self.fetch_models_button` di kedua fungsi

---

### Item #4 — Hapus Auto Retry Toggle (UI only, hardcode di backend)

**UI HAPUS** (L502-503):
```python
self.auto_retry_switch = ctk.CTkSwitch(..., text="Auto Retry?", variable=self.auto_retry_var, ...)
self.auto_retry_switch.grid(row=4, column=0, ...)
```

**Var hapus** (L146): `self.auto_retry_var = tk.BooleanVar(value=False)` → **HAPUS**

**Backend — HARDCODE `True`** di `_run_processing()` (L1399):
```python
# SEBELUM:
auto_retry_enabled = self.auto_retry_var.get()
# SESUDAH:
auto_retry_enabled = True  # Always enabled
```

**Ripple effects** — referensi ke switch yang harus dibersihkan:
| Lokasi | Baris | Aksi |
|---|---|---|
| `_disable_ui_during_processing()` | L1374 | `self.auto_retry_switch.configure(state=DISABLED)` → **HAPUS baris** |
| `_reset_ui_after_processing()` | L1545 | `self.auto_retry_switch.configure(state=NORMAL)` → **HAPUS baris** |
| `_load_settings()` | L1025 | `self.auto_retry_var.set(settings.get("auto_retry", False))` → **HAPUS** |
| `_save_settings()` | L1117 | `"auto_retry": self.auto_retry_var.get()` → **HAPUS dari dict** |

**Catatan `batch_processing.py`**: `auto_retry_enabled=False` di signature (L554) dan `if auto_retry_enabled and...` (L834) tetap dipertahankan — hanya nilai yang dikirim dari UI yang di-hardcode jadi `True`. Kode backend tidak perlu diubah.

---

### Item #5 — Tambah Custom URL Field + Resize API Key Field

**Saat ini**: API textbox `height=60`, mengisi `col=0` penuh (3 row vertikal).

**Target** (dari screenshot coret-coretan):
- API Key field → lebih pendek, bottom-nya align dengan row kedua (Provider+Stop)
- Custom URL field → sejajar dengan row ketiga (Model+Clear Log)

**Tambahan var** di `__init__`:
```python
self.base_url_var = tk.StringVar(value="")  # custom base URL per provider
```

**UI tambahan** setelah `api_textbox`:
```python
# API Key field — height dikurangi biar 2 baris (sejajar row 1+2)
self.api_textbox = ctk.CTkTextbox(api_section, height=40, ...)  # dari 60 → ~40

# URL field baru di row=2, col=0
self.base_url_entry = ctk.CTkEntry(
    api_section,
    textvariable=self.base_url_var,
    placeholder_text="Base URL (optional, e.g. https://...)",
    height=35,
    corner_radius=5,
    font=self.font_normal
)
self.base_url_entry.grid(row=2, column=0, padx=7, pady=(0, 10), sticky="ew")
```

**Integrasi dengan Provider change**:
- Saat provider berubah, `base_url_var` di-set ke default base URL provider tersebut
- `_on_provider_change()` perlu update `base_url_var`
- Saat fetch models, `_fetch_models()` pakai `base_url_var.get()` sebagai `base_url` untuk OpenAI SDK

**Load/Save settings** — tambahkan:
```python
# Di _load_settings():
self.base_url_var.set(settings.get("base_url_override", ""))

# Di _save_settings():
"base_url_override": self.base_url_var.get(),
```

**Disable/Enable saat processing**:
```python
# Di _disable_ui_during_processing():
self.base_url_entry.configure(state=tk.DISABLED)
# Di _reset_ui_after_processing():
self.base_url_entry.configure(state=tk.NORMAL)
```

---

### Ringkasan Perubahan UI

| Item | File | Scope perubahan | Catatan |
|---|---|---|---|
| Hapus button Load | `app.py` | L385-386, L1386, L1556 + fungsi L699-720 | Hapus widget + fungsi + ripple |
| Hapus button Delete | `app.py` | L391-392, L1388, L1558 + fungsi L746-813 | Hapus widget + fungsi + ripple |
| Pindah Provider dropdown | `app.py` | L395-406 (grid row/col baru) | Pindah ke row tengah sejajar Stop |
| Pindah Model dropdown | `app.py` | `settings_col2` → naik ke `api_section` | Hapus label "Models:", plain dropdown |
| Save → Fetch | `app.py` | L388-389, fungsi baru `_fetch_models` | Ganti widget + fungsi, disable saat processing |
| Hapus Auto Retry toggle | `app.py` | L146, L502-503, L1025, L1117, L1374, L1545 | UI hapus, backend hardcode `True` |
| Tambah URL field | `app.py` | Tambah var + widget + grid, update load/save/disable | Sejajar row ketiga |
| Resize API Key field | `app.py` | `height=60` → lebih kecil | Sesuaikan agar 2 baris vertikal |

---

### Keputusan UI (Open Questions → Resolved)

| Q | Keputusan |
|---|---|
| **Model dropdown kosong** | Tampilkan placeholder **"Select model..."** jika belum pernah fetch. Tidak ada default value hardcoded. |
| **Saat ganti provider** | **Restore last selected model** per-provider dari config. Tidak perlu fetch ulang. |
| **URL field** | Auto-isi URL default provider, tapi **disabled** (read-only). Hanya **enabled** jika provider = **Custom**. |

---

### Implikasi Arsitektur dari Keputusan Model & URL

#### A. Model State harus Per-Provider (bukan satu `model_var`)

Saat ini hanya ada satu `self.model_var`. Setelah refactor perlu:
```python
# Di __init__:
self.model_var = tk.StringVar(value="")           # model yang tampil di dropdown
self.models_by_provider = {}                       # cache: {provider: [model_ids]}
self.selected_model_by_provider = {}               # pilihan terakhir: {provider: model_id}
```

Logika saat provider berubah (`_on_provider_change`):
```python
def _on_provider_change(self, value):
    # 1. Simpan state provider lama
    old_provider = self.selected_provider
    self._selected_model_by_provider[old_provider] = self.model_var.get()
    
    # 2. Update provider
    self.selected_provider = value
    
    # 3. Restore model dari cache (tanpa fetch ulang)
    cached_models = self.models_by_provider.get(value, [])
    last_model = self.selected_model_by_provider.get(value, "")
    
    if cached_models:
        self.model_dropdown.configure(values=cached_models)
        self.model_dropdown.set(last_model if last_model in cached_models else cached_models[0])
    else:
        self.model_dropdown.configure(values=["Select model..."])
        self.model_dropdown.set("Select model...")
        self.model_var.set("")
    
    # 4. Update URL field
    self._update_url_field_for_provider(value)
    
    # 5. Load API keys untuk provider ini
    self._load_provider_keys(value)
```

#### B. Config JSON perlu menyimpan state per-provider

Tambahan ke `_save_settings()`:
```python
"models_by_provider": self.models_by_provider,               # {provider: [model_ids]}
"selected_model_by_provider": self.selected_model_by_provider, # {provider: model_id}
"base_url_override": self.base_url_var.get(),
```

Tambahan ke `_load_settings()`:
```python
self.models_by_provider = settings.get("models_by_provider", {})
self.selected_model_by_provider = settings.get("selected_model_by_provider", {})
self.base_url_var.set(settings.get("base_url_override", ""))

# Restore model dropdown untuk provider saat ini
current_provider = self.selected_provider
cached_models = self.models_by_provider.get(current_provider, [])
last_model = self.selected_model_by_provider.get(current_provider, "")
if cached_models:
    self.model_dropdown.configure(values=cached_models)
    self.model_dropdown.set(last_model if last_model in cached_models else "")
```

#### C. URL Field — Disable/Enable Logic

Default URLs per provider (di-hardcode di kode, bukan config):
```python
PROVIDER_BASE_URLS = {
    "Gemini":     "https://generativelanguage.googleapis.com/v1beta/openai/",
    "OpenAI":     "https://api.openai.com/v1",
    "OpenRouter": "https://openrouter.ai/api/v1",
    "Groq":       "https://api.groq.com/openai/v1",
    "KoboiLLM":   "https://litellm.koboi2026.biz.id",
    "Custom":     "",   # kosong, user isi sendiri
}
```

Logika update URL field:
```python
def _update_url_field_for_provider(self, provider):
    default_url = PROVIDER_BASE_URLS.get(provider, "")
    self.base_url_var.set(default_url)
    if provider == "Custom":
        self.base_url_entry.configure(state=tk.NORMAL,
                                      placeholder_text="Enter your Base URL...")
    else:
        self.base_url_entry.configure(state=tk.DISABLED)  # read-only
```

**Catatan penting**: URL yang dikirim ke `_fetch_models()` dan ke API call:
- Provider built-in → pakai `PROVIDER_BASE_URLS[provider]` (bukan dari field, karena field disabled)
- Provider Custom → pakai `self.base_url_var.get()`

#### D. Provider "Custom" — Perlu Ditambahkan ke Provider List

Saat ini `available_providers` = `['Gemini', 'OpenAI', 'OpenRouter', 'Groq', 'KoboiLLM']`.

Perlu tambah `"Custom"` ke list, tapi **tidak ada modul backend-nya** (Custom hanya pakai OpenAI-compat endpoint dengan URL user-defined). Dispatch di `provider_manager.get_metadata()` perlu handle case ini.

---

### Ringkasan Perubahan UI (Updated)

| Item | File | Scope | Catatan |
|---|---|---|---|
| Hapus button Load + Delete | `app.py` | L385-392, L1386-1388, L1556-1558 + 3 fungsi (~113 baris) | Clean |
| Pindah Provider dropdown | `app.py` | L395-406 → grid baru row=2 col=1+2 di `api_section` | Sejajar Stop |
| Pindah Model dropdown | `app.py` | `settings_col2` row=2 → `api_section` row=3 col=1+2 | Hapus label "Models:" |
| Save → Fetch | `app.py` | L388-389 + 3 fungsi baru | Disable saat processing |
| Hapus Auto Retry toggle | `app.py` | 6 titik + L1399 hardcode `True` | Bersih |
| Tambah URL field | `app.py` | var + widget + disable logic + save/load | Disabled kecuali Custom |
| Model per-provider state | `app.py` | `models_by_provider` + `selected_model_by_provider` | State restore tanpa re-fetch |
| Provider Custom baru | `app.py` + `provider_manager.py` | Tambah "Custom" ke list | URL dari field user |
| Resize API Key field | `app.py` | `height=60` → ~40 | Sesuaikan 2 baris |

---

## 10. Git & Dokumentasi — Analisis & Rencana

### State Saat Ini (Audit)

**Branches:** Hanya `main`. Tidak ada `dev`, tidak ada task branches.

**Commit history masalah** (dari `git log --oneline`):
```
499c47f feat: add Gemini 3.x model support... [body 7 baris mixed ke title]
1cf278c feat: Add JSON cleaning function... [body 4 baris mixed ke title]
```
Prefix konvensional ada (`feat:`, `fix:`, `docs:`), tapi body digabung ke title. `--oneline` jadi berantakan.

**Root directory issues:**
```
api_jikaperlu/        ← !! API keys di sini — HAPUS dari repo (user handle manual)
logs                  ← log file di root, tambah ke .gitignore
v3.11.1/ + *.zip      ← release artifacts 294MB+! Tambah ke .gitignore
v3.11.2/ + *.zip
v3.11.3/ + *.zip
dist_nuitka/          ← build output, tambah ke .gitignore
__pycache__/          ← sudah di .gitignore tapi mungkin ter-track
```

### Target (Mengadopsi RJ Music Studio Standard)

**Branch structure:**
```
main                              ← release/stable baseline only
dev                               ← integration branch
task/docs-governance              ← AGENTS.md + docs/ (dikerjakan PERTAMA)
task/refactor-backend             ← B1-B9, U1-U2
task/refactor-ui                  ← UI1-UI11 (setelah backend selesai)
```

**`.gitignore` tambahan yang dibutuhkan:**
```gitignore
# Build artifacts
dist_nuitka/
dist/
build/
*.zip
v*/

# Logs
logs
*.log

# API keys — jangan pernah commit
api_jikaperlu/
*.env
.env*
```

**Dokumentasi baru (`docs/` folder):**

| File | Isi |
|---|---|
| `AGENTS.md` (root) | Required reading, rules, verification steps untuk AI agent |
| `docs/ARCHITECTURE.md` | Flow provider → request → parsing → output |
| `docs/GIT_POLICY.md` | Branch rules, commit style, forbidden files |
| `docs/CURRENT_STATE.md` | Provider aktif, state build, known issues |
| `docs/HANDOFF.md` | Context handoff antar sesi agent |
| `docs/ROADMAP.md` | Phase refactoring ini + rencana selanjutnya |

---

## 11. Scope Final — Semua Item yang Akan Diimplementasi

### Backend (`src/api/`)

| # | Item | File | Estimasi |
|---|---|---|---|
| B1 | Refactor `gemini_api.py` ke OpenAI SDK + compat endpoint, hapus SDK/REST path lama | `gemini_api.py` | **Besar** (~600 baris dihapus, jadi ~150 baris) |
| B2 | OpenAI tetap Responses API, hapus dead code + commented-out debug | `openai_api.py` | Sedang |
| B3 | Hapus semua `*_MODEL_PRESETS` dict dan `DEFAULT_MODEL` hardcoded | Semua `*_api.py` | Sedang |
| B4 | Pindah `_clean_json_text()` ke `src/utils/json_utils.py` (shared) | Baru + 5 file | Kecil |
| B5 | Hapus Gemini Auto Rotation (model lock, cooldown, select_next_model, dll) | `gemini_api.py` | Bagian B1 |
| B6 | Tambah `PROVIDER_BASE_URLS` mapping constant | `provider_manager.py` | Kecil |
| B7 | Tambah handler provider `"Custom"` di dispatch | `provider_manager.py` | Kecil |
| B8 | Refactor if-elif chain dispatch ke interface seragam `module.get_metadata(...)` | `provider_manager.py` | Sedang |
| B9 | Fix duplicate `gpt-4o` di `_STRUCTURED_OUTPUT_MODEL_PREFIXES` | `openai_api.py` | Trivial |

### Utils (`src/utils/`)

| # | Item | File | Estimasi |
|---|---|---|---|
| U1 | Tambah level filter `_TERMINAL_PRINT_TAGS` di `log_message()` | `logging.py` | Kecil |
| U2 | Buat `src/utils/json_utils.py` untuk shared `_clean_json_text()` | Baru | Kecil |

### UI (`src/ui/app.py`)

| # | Item | Estimasi |
|---|---|---|
| UI1 | Hapus Load + Delete button + 3 fungsi (`_load_api_keys`, `_save_api_keys`, `_delete_selected_api_key`) | Sedang |
| UI2 | Hapus Auto Retry switch + 6 referensinya, hardcode `True` di `_run_processing()` | Kecil |
| UI3 | Ganti Save → Fetch button + 3 fungsi baru (`_fetch_models`, `_on_models_fetched`, `_on_models_fetch_error`) | Sedang |
| UI4 | Pindah Provider dropdown ke row=2 sejajar Stop | Kecil |
| UI5 | Pindah Model dropdown ke `api_section` row=3, hapus label "Models:" | Kecil |
| UI6 | Tambah URL field (`base_url_entry`), disabled kecuali provider Custom | Sedang |
| UI7 | Resize API Key textbox `height=60` → ~40 | Trivial |
| UI8 | Tambah `"Custom"` ke provider list + `_update_url_field_for_provider()` logic | Kecil |
| UI9 | Refactor model state ke per-provider: `models_by_provider`, `selected_model_by_provider` | Sedang |
| UI10 | Update `_load_settings()` + `_save_settings()` untuk state baru + `base_url_override` | Kecil |
| UI11 | Hapus semua commented-out debug code sisa | Trivial |

### Git & Docs

| # | Item |
|---|---|
| G1 | Update `.gitignore` (tambah `dist_nuitka/`, `v*/`, `*.zip`, `logs`, `api_jikaperlu/`) |
| G2 | Buat `dev` branch dari `main` |
| G3 | Buat `AGENTS.md` di root |
| G4 | Buat `docs/` folder: `ARCHITECTURE.md`, `GIT_POLICY.md`, `CURRENT_STATE.md`, `HANDOFF.md`, `ROADMAP.md` |

---

## 12. Urutan Implementasi yang Direkomendasikan

```
Phase 0 (dulu):  task/docs-governance
                  → G1 (.gitignore), G2 (dev branch), G3-G4 (docs)
                  → Merge ke dev

Phase 1:         task/refactor-backend
                  → U1, U2, B1-B9 (berurutan B1 dulu karena paling besar)
                  → Verifikasi: test request ke semua provider
                  → Merge ke dev

Phase 2:         task/refactor-ui
                  → UI1-UI11 (bisa paralel sebagian)
                  → Verifikasi: run app, test fetch models, test Custom provider
                  → Merge ke dev

Phase 3:         Merge dev → main sebagai release baru
```

> ✅ **Analisis selesai. Semua scope sudah terdokumentasi. Siap untuk dibuat agent prompt.**
