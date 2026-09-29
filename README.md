# ComicCraft - AI Comic Story Creator

ComicCraft is a FastAPI web app that generates a personalized 5-panel comic story from a prompt, complete with character, setting, tone, and art style selection, AI story outline & dialogue, panel illustration, live comic preview, and downloadable PDF export.

---

## 🌐 Deploy as a Live Web App (Free Hosting with GitHub)

Because ComicCraft is a dynamic **FastAPI (Python) backend application**, it needs a server to run AI generation and PDF exports (GitHub Pages only supports static HTML). 

You can host it **100% free** using one of the following methods directly connected to this GitHub repository:

### Option 1: Deploy on Render (Recommended)

1. Go to [Render.com](https://render.com/) and sign in with your GitHub account.
2. Click **New +** -> **Web Service**.
3. Select this repository: `ComicAI`.
4. Configure the settings:
   - **Name**: `comiccraft-webapp`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
5. Under **Environment Variables**, add:
   - `GEMINI_API_KEY`: *(Your Google Gemini API key)*
   - `HF_TOKEN`: *(Your Hugging Face API token)*
   - `IMAGE_PROVIDER`: `hf` (or `demo` for offline test mode)
   - `DEMO_MODE`: `false` (or `true` to test without keys)
6. Click **Create Web Service**.
7. Render will build and deploy your app. You will receive a public link (e.g., `https://comiccraft-webapp.onrender.com`) that anyone can open in their browser!

---

### Option 2: Deploy on Hugging Face Spaces (Free)

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Select **Docker** (Blank) or **FastAPI** as the Space SDK.
3. Choose **Public**.
4. Push or connect this repository to the Space.
5. In **Settings** -> **Variables and secrets**, add `GEMINI_API_KEY` and `HF_TOKEN`.
6. Your live web app will immediately run at `https://huggingface.co/spaces/<your-username>/<space-name>`.

---

### Option 3: Deploy on Koyeb / Railway

1. Sign up on [Koyeb](https://www.koyeb.com/) or [Railway](https://railway.app/) using GitHub.
2. Create a new service from your GitHub repository `ComicAI`.
3. Koyeb/Railway automatically detects the `Dockerfile` / `Procfile`.
4. Add your environment variables in the dashboard and deploy.

---

## 📁 Project Structure

```text
ComicCraft/
├── app/
│   ├── main.py              # FastAPI app initialization & static mount
│   ├── routes.py            # Web routes (/comic/new, /export/pdf, etc.)
│   ├── config.py            # Environment & paths configuration
│   ├── gemini_client.py     # Gemini client helper
│   ├── gemini_flash.py      # Gemini Flash outline generation
│   ├── gemini_pro.py        # Gemini Pro story & dialogue generator
│   ├── image_generator.py   # Hugging Face & demo image generation
│   ├── layout_builder.py    # Multi-panel comic layout renderer
│   └── exporters.py         # PDF export with FPDF
├── templates/
│   ├── index.html           # Comic creation form
│   ├── comic_preview.html   # Live comic viewer & reader
│   └── export_success.html  # Export confirmation page
├── static/
│   ├── panels/              # Generated comic panel images
│   ├── exports/             # Exported PDF comic books
│   └── fonts/               # Custom comic fonts
├── Dockerfile               # Container deployment configuration
├── Procfile                 # Cloud web process entrypoint
├── render.yaml              # Render blueprint deployment file
├── .env.example             # Example environment variables
├── requirements.txt         # Core Python dependencies
├── requirements-local-image.txt # Optional local Diffusers dependencies
├── run.bat                  # Windows one-click local launcher
└── README.md
```

---

## 💻 Local Development Setup

### 1. Create and activate virtual environment

**Windows PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2. Configure `.env`

Copy `.env.example` to `.env`:

```env
# Set to 'hf' for Hugging Face or 'demo' for mock panels
IMAGE_PROVIDER=hf
HF_TOKEN=your_huggingface_token
GEMINI_API_KEY=your_gemini_api_key
DEMO_MODE=false
```

### 3. Run Locally

```powershell
python -m uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.  
FastAPI Swagger docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
