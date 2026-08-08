# AI Smart Civic Services

A full-stack civic complaint management platform where citizens report local infrastructure problems and an AI pipeline classifies, prioritizes, and summarizes them for a service-team dashboard.

## Problem Statement

Municipal governments receive thousands of civic complaints daily — potholes, broken streetlights, water leaks, and more. Manual triage is slow, error-prone, and often routes complaints to the wrong department. **AI Smart Civic Services** automates this with:

- **ML-powered classification**: Instantly categorizes complaints into 7 departments and assigns priority levels
- **AI-generated summaries**: Gemini creates actionable briefs for service teams
- **Smart chatbot**: Guides citizens through effective complaint submission
- **Real-time analytics**: Dashboards with trends, department performance, and resolution metrics

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React + Vite + Tailwind)            │
│                                                                         │
│  Landing ─ Login/Signup ─ New Complaint ─ My Complaints ─ Detail       │
│  Admin Dashboard ─ Complaints Management ─ Admin Detail                │
│                          │                                              │
│                    Axios + TanStack Query                               │
└────────────────────────────┬────────────────────────────────────────────┘
                             │ REST API (JSON)
┌────────────────────────────▼────────────────────────────────────────────┐
│                        BACKEND (FastAPI + Python)                       │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ Routers: /api/auth  /api/complaints  /api/chatbot  /api/admin   │   │
│  └────────────┬────────────────┬───────────────┬───────────────────┘   │
│               │                │               │                       │
│  ┌────────────▼─┐  ┌──────────▼──────┐  ┌────▼──────────┐            │
│  │ auth_service  │  │   ai_service    │  │ gemini_service│            │
│  │ (JWT+bcrypt)  │  │ (scikit-learn)  │  │ (Gemini API)  │            │
│  └──────────────┘  │  TF-IDF→Model   │  │ Summary+Chat  │            │
│                    │  Category+Priority│  │               │            │
│                    └─────────────────┘  └───────────────┘            │
│                              │                                         │
│  ┌───────────────────────────▼─────────────────────────────────────┐   │
│  │              MongoDB (Beanie ODM / Motor async)                 │   │
│  │   Collections: users, complaints, departments                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## AI Technology

### Classification (scikit-learn) — `ai_service.py`
- **What**: Pre-trained TF-IDF + classifier models for 7-category and 4-priority classification
- **Categories**: Road, Water, Waste, Electricity, Drainage, Safety, Other
- **Priority levels**: Critical, High, Medium, Low
- **Training data**: NYC 311 service requests (adapted)
- **Preprocessing**: Lowercase → URL removal → special char removal → stopword removal (keep negations) → lemmatization
- **Limitation**: Trained on US-city data; may not generalize globally. Priority labels are rule-derived, not ground truth.

### Summarization (Gemini API) — `gemini_service.py`
- **What**: Gemini 1.5 Flash generates 1-2 sentence actionable summaries for service teams
- **Fallback**: If Gemini API fails, complaint saves with `summary: null` — non-blocking
- **Limitation**: Depends on API availability and quota; summaries may vary in quality

### Guidance Chatbot (Gemini API) — `gemini_service.py`
- **What**: Conversational AI assistant that helps citizens describe issues effectively
- **Scoped**: System prompt restricts responses to civic complaint guidance only
- **Category suggestion**: Uses the ML model (not Gemini) for suggestions; Gemini only generates clarifying questions when confidence is low

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (local or Atlas)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy .env.example to .env and fill in your values
copy .env.example .env

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy .env.example to .env
copy .env.example .env

# Start dev server
npm run dev
```

### Environment Variables

**Backend (.env)**:
| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | MongoDB connection string (Atlas or local) |
| `DATABASE_NAME` | Database name (default: `civic_db`) |
| `SECRET_KEY` | JWT signing secret (generate a random string) |
| `GEMINI_API_KEY` | Google Gemini API key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration (default: 60) |

**Frontend (.env)**:
| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Backend API URL (default: `http://localhost:8000/api`) |

### MongoDB Atlas Setup

1. Create a free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create a database user with read/write permissions
3. Add your IP to the Network Access list (or use `0.0.0.0/0` for development)
4. Get the connection string and set it as `MONGODB_URI` in your `.env`

## Running Locally

1. Start MongoDB (if using local)
2. Start the backend: `uvicorn app.main:app --reload --port 8000` (from `backend/`)
3. Start the frontend: `npm run dev` (from `frontend/`)
4. Open http://localhost:5173

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/me` | Current user profile |

### Complaints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/complaints` | Create complaint (AI pipeline) |
| GET | `/api/complaints` | List (filtered, paginated) |
| GET | `/api/complaints/{id}` | Complaint detail |
| PATCH | `/api/complaints/{id}` | Update status/department |
| DELETE | `/api/complaints/{id}` | Delete (admin only) |

### Chatbot
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chatbot/suggest` | ML category suggestion |
| POST | `/api/chatbot/message` | Gemini chat reply |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/stats` | Dashboard analytics |

## Deployment Notes

### Backend (Render / Railway)
- Set all environment variables in the platform's settings
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Ensure `ml_models/` directory with `.pkl` files is included in the deployment

### Frontend (Vercel / Netlify)
- Build command: `npm run build`
- Output directory: `dist`
- Set `VITE_API_BASE_URL` to your deployed backend URL
- Add a redirect rule: `/* → /index.html` (for SPA client-side routing)

### MongoDB Atlas
- Use the free M0 tier for development
- Set up IP allowlist (allow `0.0.0.0/0` for cloud deployment, or restrict to your backend's static IP)
- Create appropriate indexes (Beanie creates them automatically from Document settings)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, Tailwind CSS v3, Recharts, TanStack Query |
| Backend | Python, FastAPI, Beanie ODM, Motor |
| Database | MongoDB (Atlas) |
| Auth | JWT (python-jose + passlib/bcrypt) |
| ML | scikit-learn, NLTK, joblib |
| GenAI | Google Gemini API (1.5 Flash) |

## License

This project was built for a hackathon. All rights reserved.
