# 🎬 PauseCut

> ⚡ Now includes redesigned editing workspace (v2)

> AI-powered video editing workspace with automatic trimming and smart segmentation

PauseCut is an AI-assisted video editing tool that detects silence, repetition, and low-value segments to help refine long videos into clean, watchable content.

---

## ⚡ Features

- 🎧 Silence detection (audio-based)
- 🔁 Repetition detection
- ✂️ Automatic segment generation
- 🎞 Timeline-based editing interface
- 👥 Character-based filtering (face recognition)
- ⚡ Fast preview rendering
- 🎯 Smart editing modes

---

## 🧠 How it works

1. Paste a video link
2. PauseCut analyzes audio and patterns
3. Segments are generated automatically
4. You review and refine edits
5. Export the final video

---

## 🖥️ Workspace

PauseCut provides a professional editing environment:

- Program monitor (video preview)
- Timeline with segments
- AI-generated cuts
- Character selection panel
- Export-ready pipeline

---

## ⚙️ Tech Stack

- **Frontend:** Next.js + TailwindCSS  
- **Backend:** FastAPI  
- **Processing:** FFmpeg  

---

## 🚀 Getting Started

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/EfeElbeyli/pausecut.git
cd pausecut
```

---

### 2. Backend setup (FastAPI)

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend will run at:
👉 http://localhost:8000

---

### 3. Frontend setup (Next.js)

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will run at:
👉 http://localhost:3000

---

### 4. Open the app

Go to:
👉 http://localhost:3000

Paste a video link and start analyzing 🚀

## 🐳 Run with Docker (optional)

```bash
docker-compose up --build
```

