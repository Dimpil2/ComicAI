# ComicCraft - AI Comic Story Creator

ComicCraft is a FastAPI web app that follows the supplied project document: user prompt + character + setting + tone + art style -> 5-panel outline -> narration/dialogue -> panel illustrations -> comic preview -> PDF export.

## Project structure

```text
ComicCraft/
├── app/
│   ├── main.py
│   ├── routes.py
│   ├── config.py
│   ├── gemini_client.py
│   ├── gemini_flash.py
│   ├── gemini_pro.py
│   ├── image_generator.py
│   ├── layout_builder.py
│   └── exporters.py
├── templates/
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
├── static/
│   ├── panels/
│   ├── exports/
│   └── fonts/
├── .env.example
├── requirements.txt
├── requirements-local-image.txt
├── run.bat
└── README.md
```

## 1. Create the environment

Windows PowerShell:

```powershell
cd C:\path\to\ComicCraft
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 2. Configure `.env`

Copy `.env.example` to `.env`.

For a first test, keep:

```env
IMAGE_PROVIDER=demo
DEMO_MODE=true
```

The app will run and create placeholder panel images without any API keys.

For real Gemini text generation:

```env
GEMINI_API_KEY=YOUR_KEY
DEMO_MODE=false
```

For hosted Hugging Face image generation:

```env
IMAGE_PROVIDER=hf
HF_TOKEN=YOUR_TOKEN
DEMO_MODE=false
```

## 3. Run

```powershell
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

FastAPI docs: `http://127.0.0.1:8000/docs`

## 4. Optional local Stable Diffusion mode

The supplied document uses Hugging Face Diffusers + Stable Diffusion. On a machine with enough local compute, install the extra dependencies:

```powershell
python -m pip install -r requirements-local-image.txt
```

Then set:

```env
IMAGE_PROVIDER=diffusers
DEMO_MODE=false
```

## Notes on the supplied reference

The source document specifies FastAPI, Gemini Flash for structured outlines, Gemini Pro for detailed story text, Stable Diffusion for images, Jinja2 templates, and FPDF PDF export. This implementation keeps that architecture while using the current `google-genai` Python SDK and configurable current Gemini model IDs.
