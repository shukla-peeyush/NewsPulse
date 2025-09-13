# NewsPulse - Full Stack News Aggregation Platform

A modern news aggregation platform built with FastAPI (backend) and React (frontend).

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### 1. Install Dependencies
```bash
# Install root dependencies (for development scripts)
npm install

# Install all project dependencies
npm run install-all
```

### 2. Setup Backend Environment
```bash
cd BackEnd
# Activate virtual environment (if not already created)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Run Both Applications
```bash
# From root directory - runs both frontend and backend
npm run dev
```

This will start:
- **Backend**: http://localhost:8000 (API + Documentation at /docs)
- **Frontend**: http://localhost:5173 (React app)

## 🛠️ Individual Commands

### Backend Only
```bash
npm run backend
# OR
cd BackEnd && python run_server.py
```

### Frontend Only
```bash
npm run frontend
# OR
cd FrontEnd/news-app && npm run dev
```

## 📁 Project Structure

```
├── BackEnd/                 # FastAPI Backend
│   ├── src/
│   │   ├── api/            # API endpoints
│   │   ├── auth/           # Authentication
│   │   ├── classifier/     # ML classification
│   │   ├── storage/        # Database models
│   │   └── ...
│   ├── requirements.txt    # Python dependencies
│   └── run_server.py      # Backend startup
│
├── FrontEnd/news-app/      # React Frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API integration
│   │   └── ...
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Vite config
│
├── package.json           # Root dev scripts
└── README.md             # This file
```

## 🔧 Development

### API Integration
The frontend is pre-configured to connect to the backend API at `http://localhost:8000`. The API service layer is located in `FrontEnd/news-app/src/services/api.js`.

### Available Endpoints
- **GET /**: API information
- **GET /health**: System health check
- **GET /articles**: Get articles with filtering
- **GET /sources**: List news sources
- **GET /categories**: Get article categories
- **POST /scrape**: Trigger manual scraping

### Database
The backend uses SQLite by default with the database file at `BackEnd/data/newspulse.db`.

## 🚀 Production Build

```bash
# Build frontend for production
npm run build

# The built files will be in FrontEnd/news-app/dist/
```

## 🔍 Troubleshooting

1. **Port conflicts**: If ports 8000 or 5173 are in use, modify the configurations in:
   - Backend: `BackEnd/run_server.py`
   - Frontend: `FrontEnd/news-app/vite.config.js`

2. **CORS issues**: The backend should be configured for CORS. Check `BackEnd/src/api/main_simple.py` for CORS settings.

3. **Dependencies**: Make sure all dependencies are installed with `npm run install-all`.