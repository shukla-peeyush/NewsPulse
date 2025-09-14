# NewsPulse - Full Stack News Aggregation Platform

A modern news aggregation platform built with FastAPI (backend) and React (frontend), featuring intelligent ML-based article classification for the fintech/payments industry.

## 🚀 Quick Start for New Users

### Prerequisites
- **Python 3.9+** (with pip)
- **Node.js 16+** (with npm)
- **Git** (for cloning)

### 1. Clone the Repository
```bash
git clone https://github.com/shukla-peeyush/NewsPulse.git
cd NewsPulse
```

## 🖥️ Cross-Platform Setup

### Windows Users

#### Option A: Using Batch Script (Easiest)
```cmd
cd BackEnd
start.bat
```

#### Option B: Manual Setup
```cmd
cd BackEnd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python scripts\init_database.py
python run_server.py
```

### macOS/Linux Users

#### Option A: Using Shell Script (Easiest)
```bash
cd BackEnd
chmod +x start.sh
./start.sh
```

#### Option B: Manual Setup
```bash
cd BackEnd
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/init_database.py
python run_server.py
```

### Universal Python Script (All Platforms)
```bash
cd BackEnd
python start.py  # Works on Windows, macOS, and Linux
```

## 🔧 Backend Services

### 1. API Server
```bash
# Start the main API server
cd BackEnd
python run_server.py
# Server available at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### 2. RSS Fetcher (News Collection)
```bash
# Fetch articles from RSS feeds
cd BackEnd
python scripts/run_fetcher.py
```

### 3. ML Classifier (Article Classification)
```bash
# Classify articles using ML models
cd BackEnd
python scripts/run_classifier.py
```

### 4. Database Initialization
```bash
# Set up database with sample sources
cd BackEnd
python scripts/init_database.py
```

## ⚛️ Frontend Setup

### All Platforms
```bash
# Navigate to frontend directory
cd FrontEnd/news-app

# Install dependencies
npm install

# Start development server
npm run dev
# Frontend available at: http://localhost:5173
```

## 🛠️ Complete Development Workflow

### Option 1: Automated Setup (Recommended)
```bash
# From root directory
npm install              # Install root dev dependencies
npm run install-all      # Install both backend and frontend deps
npm run dev             # Start both services simultaneously
```

### Option 2: Manual Setup
```bash
# Terminal 1 - Backend
cd BackEnd
python start.py         # Cross-platform startup

# Terminal 2 - Frontend  
cd FrontEnd/news-app
npm run dev

# Terminal 3 - Data Collection (Optional)
cd BackEnd
python scripts/run_fetcher.py      # Fetch news articles
python scripts/run_classifier.py   # Classify articles
```

## 📁 Project Structure

```
NewsPulse/
├── 📄 Root Configuration
│   ├── package.json          # Root dev scripts & dependencies
│   ├── .gitignore            # Git ignore rules
│   └── README.md             # This file
│
├── 🐍 BackEnd/               # Python FastAPI Backend
│   ├── src/
│   │   ├── api/              # FastAPI endpoints & routing
│   │   ├── auth/             # Authentication & authorization
│   │   ├── classifier/       # ML-based article classification
│   │   ├── storage/          # Database models & management
│   │   ├── fetcher/          # RSS feed processing
│   │   ├── extractor/        # Content extraction utilities
│   │   ├── monitoring/       # Logging & metrics
│   │   ├── cache/            # Redis caching layer
│   │   └── utils/            # Shared utilities
│   ├── scripts/              # Cross-platform utility scripts
│   │   ├── init_database.py  # Database setup
│   │   ├── run_fetcher.py    # RSS feed fetcher
│   │   └── run_classifier.py # ML article classifier
│   ├── data/                 # SQLite database storage
│   ├── requirements.txt      # Python dependencies (cross-platform)
│   ├── .env.example          # Environment template
│   ├── start.py              # Cross-platform startup script
│   ├── start.bat             # Windows batch script
│   ├── start.sh              # Unix/Linux/macOS shell script
│   └── run_server.py         # Main server entry point
│
└── ⚛️ FrontEnd/news-app/     # React + Vite Frontend
    ├── src/
    │   ├── components/       # React UI components
    │   ├── services/         # API integration layer
    │   └── assets/           # Static assets
    ├── public/               # Public assets & dummy data
    ├── package.json          # Frontend dependencies
    └── vite.config.js        # Vite configuration
```

## 🔧 Available Commands

### Root Level Commands
```bash
npm run dev              # Run both frontend and backend
npm run backend          # Run backend only  
npm run frontend         # Run frontend only
npm run install-all      # Install all dependencies
npm run build           # Build frontend for production
```

### Backend Commands (Cross-Platform)
```bash
cd BackEnd

# Server Management
python start.py                    # Cross-platform startup
python run_server.py              # Start API server only

# Data Management  
python scripts/init_database.py   # Initialize database
python scripts/run_fetcher.py     # Fetch RSS articles
python scripts/run_classifier.py  # Classify articles with ML

# Platform-Specific Quick Start
# Windows:
start.bat

# macOS/Linux:
./start.sh
```

### Frontend Commands
```bash
cd FrontEnd/news-app
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

## 🔗 API Endpoints

### Core Endpoints
- **GET /**: API information and welcome message
- **GET /health**: System health check with database statistics
- **GET /articles**: Get articles with filtering and pagination
- **GET /articles/{id}**: Get specific article by ID
- **GET /sources**: List all news sources
- **GET /categories**: Get article categories with counts
- **GET /stats**: Platform statistics and metrics

### Query Parameters for /articles
- `skip`: Number of articles to skip (pagination)
- `limit`: Maximum articles to return (max 1000)
- `min_relevance_score`: Filter by minimum relevance score
- `category`: Filter by article category
- `source_id`: Filter by news source ID

## 🗄️ Database

The application uses **SQLite** by default for development, with **PostgreSQL** support for production.

### Database Models
- **NewsSource**: RSS feeds and news websites
- **Article**: News articles with ML classification
- **ScrapingSession**: RSS processing session tracking

### Database Location
- **Windows**: `BackEnd\data\newspulse.db`
- **macOS/Linux**: `BackEnd/data/newspulse.db`
- **Production**: Configurable via `DATABASE_URL` environment variable

## 🔐 Environment Configuration

Copy `BackEnd/.env.example` to `BackEnd/.env` and configure:

```bash
# Application Settings
APP_NAME=NewsPulse
DEBUG=false

# Server Configuration
HOST=127.0.0.1
PORT=8000

# Database Configuration
DATABASE_URL=sqlite:///./data/newspulse.db

# Security Settings
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 🤖 Machine Learning Features

### Automatic Article Classification
The system uses advanced ML models to automatically categorize news articles:

- **FinBERT**: Financial domain-specific BERT model
- **Custom Models**: Trained on fintech/payments data
- **Categories**: PAYMENTS, FUNDING, REGULATION, PRODUCT LAUNCH, etc.
- **Relevance Scoring**: 0-100 relevance score for each article

### Running ML Classification
```bash
cd BackEnd
python scripts/run_classifier.py
```

## 🔄 Data Collection Workflow

### 1. Initialize Database
```bash
python scripts/init_database.py
```

### 2. Fetch Articles
```bash
python scripts/run_fetcher.py
```

### 3. Classify Articles
```bash
python scripts/run_classifier.py
```

### 4. View Results
- API: http://localhost:8000/articles
- Frontend: http://localhost:5173

## 🚀 Production Deployment

### Build for Production
```bash
# Build frontend
npm run build

# The built files will be in FrontEnd/news-app/dist/
```

### Environment Setup
1. Set `DEBUG=false` in `.env`
2. Configure production database URL
3. Set secure `SECRET_KEY`
4. Configure appropriate `CORS_ORIGINS`
5. Set up Redis for caching (optional)

## 🔍 Troubleshooting

### Common Issues

#### 1. Python Virtual Environment Issues
```bash
# Windows
cd BackEnd
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# macOS/Linux
cd BackEnd
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Port Conflicts
- **Backend (8000)**: Modify `BackEnd/run_server.py`
- **Frontend (5173)**: Modify `FrontEnd/news-app/vite.config.js`

#### 3. Database Issues
```bash
# Windows
cd BackEnd
del data\newspulse.db
python scripts\init_database.py

# macOS/Linux
cd BackEnd
rm -f data/newspulse.db
python scripts/init_database.py
```

#### 4. Node.js Dependency Issues
```bash
cd FrontEnd/news-app
rm -rf node_modules package-lock.json  # macOS/Linux
rmdir /s node_modules & del package-lock.json  # Windows
npm install
```

#### 5. Cross-Platform Path Issues
- Use the `start.py` script instead of platform-specific commands
- Ensure you're using forward slashes in Python paths
- Use `pathlib.Path` for cross-platform file operations

### Platform-Specific Notes

#### Windows
- Use `python` instead of `python3`
- Use `venv\Scripts\activate` for virtual environment
- Use `start.bat` for quick startup

#### macOS/Linux
- Use `python3` for Python commands
- Use `source venv/bin/activate` for virtual environment
- Use `./start.sh` for quick startup
- Make shell scripts executable: `chmod +x start.sh`

### Getting Help

- Check the API documentation at http://localhost:8000/docs
- Review logs in `BackEnd/backend.log`
- Ensure all dependencies are installed with `npm run install-all`
- Use the cross-platform `start.py` script for consistent behavior

## 🧪 Development Notes

### Technology Stack
- **Backend**: FastAPI, SQLAlchemy, PyTorch, Transformers
- **Frontend**: React 19, Vite, Tailwind CSS
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **ML**: FinBERT for financial text classification
- **Caching**: Redis (optional)

### Code Quality
- Backend: Python type hints, async/await patterns
- Frontend: Modern React hooks, TypeScript-ready
- Linting: ESLint for frontend, Python best practices
- Error handling: Comprehensive error boundaries and logging

### Cross-Platform Compatibility
- Unified requirements.txt without platform-specific paths
- Cross-platform startup scripts (Python, Batch, Shell)
- Path handling using pathlib for Windows/Unix compatibility
- Platform detection and appropriate command selection

---

**Happy coding! 🚀**

For issues or contributions, please visit the [GitHub repository](https://github.com/shukla-peeyush/NewsPulse).