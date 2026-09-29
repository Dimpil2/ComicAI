# ComicCraft - AI Comic Story Creator using Gemini Models

ComicCraft is a web-based application that uses AI to generate personalized comic book stories and illustrations based on user-provided prompts. Built with **FastAPI** and integrated with **Google Gemini AI models** along with **Stable Diffusion**, ComicCraft streamlines the creative process of generating storylines, dialogues, and vivid comic-style imagery automatically.

The application takes in user information—such as story prompt, main character name, setting, tone, and art style—and generates a panel-by-panel storyline and corresponding illustrations. Users can view the comic preview directly on the web interface and download the full comic in PDF format, structured with both images and narration.

---

## 📖 Key User Scenarios

* **Scenario 1 (Personalized Storytelling):** A user enters a prompt describing their comic story, such as *"A brave fox exploring an enchanted forest."* The system uses this input to generate a complete 5-panel comic strip, including multiple panels with accompanying images and text. The user also specifies preferences like the main character’s name, the setting (e.g., forest), tone (e.g., dramatic), and art style (e.g., realistic). The system combines Gemini for story generation and Stable Diffusion for image creation to produce a visually immersive comic strip.
* **Scenario 2 (Iterative Customization):** A user wants a light-hearted, cartoonish feel. On the input form, they select *"funny"* as the tone and *"comic book"* as the art style. When submitted, the system regenerates the entire pipeline tailored to produce a humorous narrative and a classic comic-book aesthetic.
* **Scenario 3 (PDF Compilation & Export):** After reviewing the on-screen preview of their comic, the user clicks **Download Your Comic as PDF**. The system uses `layout_builder.py` to assemble the layout and `exporters.py` to compile the comic into a downloadable PDF via FPDF, placing images and narrative text onto consecutive pages. The user is then redirected to the export confirmation page.

---

## 🏛️ System Architecture

```
User (Browser)
      │
      ▼
FastAPI Backend (app/main.py)
      │
      ├──► HTML Templating (Jinja2 + CSS) ──► index.html (Input Form)
      │
      └──► AI Comic Generation Logic (routes.py)
            │
            ├──► Gemini Flash (google-genai) ──► 5-Panel Structured Outline
            ├──► Gemini Pro (google-genai)   ──► Story Narration & Dialogues
            └──► Stable Diffusion / HF       ──► Panel-wise Illustrations
                        │
                        ▼
                  Layout Builder (app/layout_builder.py)
                        │
                        ▼
                  Comic Exporter (app/exporters.py ──► PDF via FPDF)
                        │
                        ▼
                  Comic Preview Page (templates/comic_preview.html)
                        │
                        ▼
                  Export Success Page (templates/export_success.html)
```

---

## 📁 Project Structure

```text
ComicCraft/
├── app/
│   ├── __init__.py          # Python package initializer
│   ├── main.py              # FastAPI application setup and routing mounts
│   ├── routes.py            # API & web route handlers (/generate, /download, etc.)
│   ├── config.py            # Dynamic paths & environment variable configuration
│   ├── gemini_client.py     # Gemini client initialization
│   ├── gemini_flash.py      # 5-panel comic outline generator using Gemini Flash
│   ├── gemini_pro.py        # Story narration, caption & dialogue generator using Gemini Pro
│   ├── image_generator.py   # Panel image creation (Demo canvas, Hugging Face, or Diffusers)
│   ├── layout_builder.py    # Layout assembly connecting artwork, outlines, and dialogues
│   └── exporters.py         # Multi-page PDF compilation using FPDF
├── api/
│   └── index.py             # Vercel serverless function entrypoint
├── templates/
│   ├── index.html           # Comic creation input form
│   ├── comic_preview.html   # Sequential 5-panel comic reader with embedded artwork
│   └── export_success.html  # Export & download confirmation page
├── static/
│   ├── panels/              # Generated comic panel images
│   ├── exports/             # Exported PDF comic books
│   └── fonts/               # Custom font files for PDF rendering
├── Dockerfile               # Production Docker container definition
├── Procfile                 # Cloud PaaS process definition
├── render.yaml              # Render 1-click blueprint deployment file
├── vercel.json              # Vercel serverless configuration
├── .env.example             # Example environment variable template
├── requirements.txt         # Core production dependencies
├── requirements-local-image.txt # Optional local PyTorch/Diffusers dependencies
├── run.bat                  # One-click Windows local launcher
├── smoke_test.py            # Automated end-to-end pipeline verification test
└── README.md
```

---

## 🛠️ Local Development Setup

### 1. Create and Activate Virtual Environment

**Windows PowerShell:**
```powershell
cd ComicCraft
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**macOS / Linux:**
```bash
cd ComicCraft
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure Environment Variables (`.env`)

Copy `.env.example` to `.env`:

```env
# Out-of-the-box demo mode (runs locally without any API keys)
DEMO_MODE=true
IMAGE_PROVIDER=demo

# For live AI text generation with Google Gemini:
GEMINI_API_KEY=YOUR_GOOGLE_GEMINI_API_KEY
DEMO_MODE=false

# For cloud image generation with Hugging Face:
IMAGE_PROVIDER=hf
HF_TOKEN=YOUR_HUGGINGFACE_TOKEN
```

### 3. Run Locally

```powershell
python -m uvicorn app.main:app --reload
```

* **Web Application:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Interactive Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🚀 Cloud Deployment Options

### Option 1: Vercel (Serverless)

1. Connect your repository to **[Vercel](https://vercel.com)**.
2. In Project **Settings** $\rightarrow$ **Environment Variables**, set:
   - `GEMINI_API_KEY`: *(Your Google Gemini API Key)*
   - `HF_TOKEN`: *(Your Hugging Face Token)*
   - `IMAGE_PROVIDER`: `hf` (or `demo`)
   - `DEMO_MODE`: `false` (or `true`)
3. Vercel automatically deploys using the included `vercel.json` and `api/index.py` with full serverless `/tmp` file handling.

### Option 2: Render (Free Cloud Web Service)

1. Sign in to **[Render.com](https://render.com/)** with GitHub.
2. Click **New +** $\rightarrow$ **Web Service** and select this repository.
3. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add your environment variables (`GEMINI_API_KEY`, `HF_TOKEN`, `IMAGE_PROVIDER=hf`, `DEMO_MODE=false`).
5. Click **Create Web Service** to get a public `https://<app>.onrender.com` URL.

### Option 3: Hugging Face Spaces / Docker

Use the included `Dockerfile` to deploy anywhere with container support:
```bash
docker build -t comiccraft .
docker run -p 7860:7860 -e DEMO_MODE=true comiccraft
```

---

## 🧪 Automated Testing

Run the automated smoke test to verify all 5 milestones end-to-end:
```powershell
python smoke_test.py
```
Outputs:
```text
Smoke test passed
Panels: 5
PDF: static/exports/comic_...pdf
```
