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

### 2. Backend Setup
```bash
# Navigate to backend directory
cd BackEnd

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
# Edit .env file with your settings if needed

# Initialize database (optional - will be created automatically)
python init_database.py
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory (from root)
cd FrontEnd/news-app

# Install Node.js dependencies
npm install
```

### 4. Run the Application

#### Option A: Run Both Services Simultaneously (Recommended)
```bash
# From root directory
npm install  # Install root dev dependencies
npm run dev  # Starts both backend and frontend
```

#### Option B: Run Services Individually
```bash
# Terminal 1 - Backend
cd BackEnd
source venv/bin/activate  # Activate virtual environment
python run_server.py

# Terminal 2 - Frontend
cd FrontEnd/news-app
npm run dev
```

### 5. Access the Application
- **Frontend**: http://localhost:5173 (React app)
- **Backend API**: http://localhost:8000 (FastAPI server)
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health

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
│   ├── data/                 # SQLite database storage
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example          # Environment template
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

## 🔧 Development Features

### Backend Capabilities
- **RSS Feed Aggregation**: Async processing of multiple news sources
- **ML Classification**: FinBERT + custom models for article categorization
- **Content Deduplication**: SHA256-based duplicate detection
- **RESTful API**: Comprehensive endpoints with pagination and filtering
- **Authentication**: JWT-based user management
- **Caching**: Redis integration for performance
- **Monitoring**: Logging and metrics collection

### Frontend Features
- **Responsive Design**: Mobile-first with Tailwind CSS
- **Dark Mode**: System preference detection and toggle
- **Real-time Search**: Client-side filtering and search
- **User Preferences**: Category saving and personalization
- **Bookmark System**: Article saving functionality
- **Modal System**: Detailed article viewing
- **Error Handling**: Comprehensive error boundaries

## 🛠️ Available Commands

### Root Level Commands
```bash
npm run dev          # Run both frontend and backend
npm run backend      # Run backend only
npm run frontend     # Run frontend only
npm run install-all  # Install all dependencies
npm run build        # Build frontend for production
```

### Backend Commands
```bash
cd BackEnd
python run_server.py           # Start API server
python run_fetcher.py          # Run RSS fetcher
python run_ml_classifier.py    # Run ML classification
python init_database.py        # Initialize database
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
- Development: `BackEnd/data/newspulse.db`
- Production: Configurable via `DATABASE_URL` environment variable

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

1. **Port conflicts**: 
   - Backend (8000): Modify `BackEnd/run_server.py`
   - Frontend (5173): Modify `FrontEnd/news-app/vite.config.js`

2. **Python virtual environment issues**:
   ```bash
   # Recreate virtual environment
   cd BackEnd
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Node.js dependency issues**:
   ```bash
   # Clear npm cache and reinstall
   cd FrontEnd/news-app
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Database issues**:
   ```bash
   # Reset database
   cd BackEnd
   rm -f data/newspulse.db
   python init_database.py
   ```

5. **CORS issues**: 
   - Check `BackEnd/src/api/main_simple.py` for CORS settings
   - Ensure frontend URL is in `CORS_ORIGINS` environment variable

### Getting Help

- Check the API documentation at http://localhost:8000/docs
- Review logs in `BackEnd/backend.log`
- Ensure all dependencies are installed with `npm run install-all`

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

---

**Happy coding! 🚀**

For issues or contributions, please visit the [GitHub repository](https://github.com/shukla-peeyush/NewsPulse).