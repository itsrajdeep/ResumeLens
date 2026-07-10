# 📄 ResumeAtlas

> **Discover, explore, and learn from real-world anonymized resumes — powered by AI.**

ResumeAtlas is an open-source platform that crawls resume-sharing communities on Reddit (e.g. r/EngineeringResumes, r/resumes), anonymizes them using Gemini AI, extracts structured skill data, and presents them through a beautiful searchable UI.

---

## ✨ Features

- 🔍 **Smart Crawler** — Incremental Reddit sync that finds resume posts and downloads PDF/image files
- 🤖 **AI-Powered Processing** — Gemini 2.5 Flash parses, summarizes, and categorizes every resume
- 🔒 **Anonymization** — PII is stripped before any resume is stored or displayed
- 🧠 **Vector Search** — Semantic similarity via Qdrant embeddings
- 📊 **Skill Analytics** — Track trending technologies, top skills by category, and more
- 🗂️ **Category Browsing** — Filter resumes by role: Frontend, Backend, AI/ML, DevOps, etc.
- ⚡ **Real-time Stats** — Live category and skill distribution charts

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React + Vite, Vanilla CSS |
| **Backend** | FastAPI (Python 3.11) |
| **Database** | PostgreSQL 16 |
| **Vector DB** | Qdrant |
| **Cache** | Redis 7 |
| **AI** | Google Gemini 2.5 Flash |
| **Crawler** | Reddit JSON API |
| **Containers** | Docker + Docker Compose |

---

## 🚀 Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/resume-atlas.git
cd resume-atlas
```

### 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in your credentials:

```env
GEMINI_API_KEY=your-gemini-api-key-here
POSTGRES_PASSWORD=your-secure-password
```

All other values have safe defaults and can be left as-is for local development.

### 3. Start all services

```bash
docker compose up --build
```

This starts:
- **PostgreSQL** on port `5432`
- **Qdrant** on ports `6333` / `6334`
- **Redis** on port `6379`
- **FastAPI backend** on port `8000`

### 4. Trigger the first crawl

```bash
curl -X POST http://localhost:8000/api/crawl/trigger
```

Or open the UI at `http://localhost:5173` and click **"Start Crawl"** from the dashboard.

---

## 📁 Project Structure

```
resume-atlas/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── crawl.py       # Crawl trigger & status endpoints
│   │   │       └── resumes.py     # Resume list, detail & stats endpoints
│   │   ├── crawler/
│   │   │   ├── reddit_client.py   # Reddit JSON API pagination
│   │   │   ├── post_filter.py     # Resume post detection & parsing
│   │   │   ├── downloader.py      # PDF/image download with dedup
│   │   │   └── sync.py            # Incremental subreddit sync engine
│   │   ├── models/
│   │   │   ├── post.py            # Reddit post DB model
│   │   │   ├── resume.py          # Processed resume DB model
│   │   │   ├── skill.py           # Skills & ResumeSkill junction
│   │   │   ├── project.py         # Projects extracted from resumes
│   │   │   └── sync_state.py      # Per-subreddit crawl state
│   │   ├── schemas/               # Pydantic response schemas
│   │   ├── config.py              # Settings (loaded from .env)
│   │   ├── database.py            # SQLAlchemy engine & session
│   │   └── main.py                # FastAPI app entry point
│   ├── alembic/                   # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                      # React + Vite app
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🌐 API Reference

The API is self-documented. With the backend running, visit:

| URL | Description |
|---|---|
| `http://localhost:8000/docs` | Swagger UI (interactive API docs) |
| `http://localhost:8000/redoc` | ReDoc API reference |

### Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/crawl/trigger` | Start a background crawl |
| `GET` | `/api/crawl/status` | Check per-subreddit sync state |
| `GET` | `/api/resumes/` | List resumes (with `?category=` & pagination) |
| `GET` | `/api/resumes/{id}` | Get a single resume detail |
| `GET` | `/api/resumes/stats/categories` | Resume counts per category |
| `GET` | `/api/resumes/stats/skills` | Top skills by usage |

---

## ⚙️ Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | *(required)* | Your Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model to use |
| `POSTGRES_USER` | `postgres` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password |
| `POSTGRES_DB` | `resume_atlas` | Database name |
| `POSTGRES_PORT` | `5432` | PostgreSQL host port |
| `QDRANT_PORT` | `6333` | Qdrant HTTP port |
| `BACKEND_PORT` | `8000` | FastAPI host port |
| `STORAGE_PATH` | `./storage` | Local file storage path |
| `REDDIT_USER_AGENT` | `ResumeAtlas/1.0` | Reddit API user agent |

---

## 🛠️ Development

### Running backend locally (without Docker)

```bash
cd backend
pip install -r requirements.txt

# Make sure Postgres, Qdrant & Redis are running, then:
uvicorn app.main:app --reload --port 8000
```

### Running database migrations

```bash
cd backend
alembic upgrade head
```

### Logs

```bash
# View all service logs
docker compose logs -f

# Backend only
docker compose logs -f backend
```

---

## 🔒 Privacy & Ethics

- All resumes are **anonymized** before storage — names, emails, phone numbers, and other PII are removed by Gemini AI before any data is saved.
- Source Reddit posts link back to the **original author's post** for attribution.
- This project is built for **educational purposes** to help job seekers understand what strong resumes look like across different roles.
- No resume data is shared with third parties.

---

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">Built with ❤️ using FastAPI, Gemini AI, and React</p>
