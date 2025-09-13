# NewsPulse - News Intelligence Platform

A sophisticated news intelligence platform that scrapes, processes, and analyzes articles from regional sources with advanced filtering and summary capabilities.

## 🚀 Features

- **📰 RSS-Based News Scraping**: Fetches articles from 4 active regional news sources using official RSS feeds
- **🔍 Smart Content Filtering**: Returns only articles with meaningful summaries (94 out of 194 articles)
- **📄 Individual Article Summaries**: Dedicated endpoint for detailed article summaries
- **👤 User Management**: Secure user registration and JWT authentication
- **📚 Saved Articles**: Personal article collections with custom notes
- **⚡ Real-time API**: FastAPI-based REST API with automatic documentation
- **🗄️ Database Storage**: SQLite database with 194+ articles and user management
- **🏥 Health Monitoring**: Comprehensive health checks and statistics

## 📊 Current Data

- **Total Articles**: 194
- **Articles with Summaries**: 94 (48.5%)
- **News Sources**: 4 active regional sources (1 disabled)
- **👤 Users**: Unlimited user registration
- **📚 Saved Articles**: Personal collections per user
- **Database**: SQLite with optimized schema + user management

## 🔗 API Endpoints

### Core Endpoints

#### 1. Get Articles (Filtered)
```http
GET /articles
```
**New Feature**: Only returns articles that have summary data (94 articles)

**Query Parameters**:
- `limit` (int): Maximum articles to return (default: 100, max: 1000)
- `skip` (int): Number of articles to skip (default: 0)
- `min_relevance_score` (float): Minimum relevance score filter
- `category` (string): Filter by primary category
- `source_id` (int): Filter by specific news source
- `processed_only` (bool): Return only processed articles

**Example Response**:
```json
[
  {
    "id": "d40a96891ee24de69e746ca5e1df3936",
    "title": "Asia's coders answer America's call",
    "url": "https://www.techinasia.com/asias-coders-answer-americas-call",
    "summary": "Asia's devs are drawing US firms. Meanwhile, our archived interview on Apple's China ties feels timely with its latest product launch.",
    "published_date": "2025-09-12T09:30:31",
    "source_name": "Tech in Asia",
    "relevance_score": null,
    "primary_category": null
  }
]
```

#### 2. Get Article Summary (New)
```http
GET /articles/{article_id}/summary
```
**Purpose**: Returns detailed summary information for a specific article

**Example Response**:
```json
{
  "id": "d40a96891ee24de69e746ca5e1df3936",
  "title": "Asia's coders answer America's call",
  "summary": "Asia's devs are drawing US firms. Meanwhile, our archived interview on Apple's China ties feels timely with its latest product launch.",
  "content": null,
  "url": "https://www.techinasia.com/asias-coders-answer-americas-call",
  "published_date": "2025-09-12T09:30:31",
  "source_name": "Tech in Asia"
}
```

#### 3. Health Check
```http
GET /health
```
**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-09-13T09:14:15.741311",
  "total_articles": 194,
  "total_sources": 5
}
```

### 👤 User Management Endpoints

- `POST /auth/register` - Register new user
- `POST /auth/login` - User authentication (returns JWT token)
- `GET /auth/me` - Get current user information

### 📚 Saved Articles Endpoints

- `POST /users/saved-articles` - Save an article to personal collection
- `GET /users/saved-articles` - Get user's saved articles
- `PUT /users/saved-articles/{id}` - Update saved article notes
- `DELETE /users/saved-articles/{id}` - Remove saved article
- `GET /users/saved-articles/count` - Get count of saved articles

### 👤 User Management Endpoints

- `POST /auth/register` - Register new user account
- `POST /auth/login` - User authentication (returns JWT token)
- `GET /auth/me` - Get current user information

### 📚 Saved Articles Endpoints

- `POST /users/saved-articles` - Save an article to personal collection
- `GET /users/saved-articles` - Get user's saved articles
- `PUT /users/saved-articles/{id}` - Update saved article notes
- `DELETE /users/saved-articles/{id}` - Remove saved article
- `GET /users/saved-articles/count` - Get count of saved articles

### Additional Endpoints

- `GET /` - API information
- `GET /articles/{article_id}` - Get specific article details
- `GET /sources` - List all news sources
- `GET /sources/{source_id}/articles` - Get articles from specific source
- `GET /stats` - Platform statistics
- `GET /categories` - Available article categories
- `POST /scrape` - Trigger manual RSS scraping

## 🛠 Quick Start

### Prerequisites
- Python 3.9+
- SQLite database (included)

### Installation & Setup

1. **Clone and Navigate**:
```bash
git clone <repository-url>
cd BackEnd
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Start the Server**:
```bash
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8002 --reload
```

4. **Access the API**:
- **API Base URL**: http://127.0.0.1:8002
- **Interactive Docs**: http://127.0.0.1:8002/docs
- **Health Check**: http://127.0.0.1:8002/health

## 📝 Usage Examples

### Get Articles with Summaries
```bash
curl -X GET "http://127.0.0.1:8002/articles?limit=5" -H "accept: application/json"
```

### Get Specific Article Summary
```bash
curl -X GET "http://127.0.0.1:8002/articles/d40a96891ee24de69e746ca5e1df3936/summary" -H "accept: application/json"
```

### Check System Health
```bash
curl -X GET "http://127.0.0.1:8002/health" -H "accept: application/json"
```

## 🏗 Architecture

### Core Components

1. **API Layer** (`src/api/main.py`)
   - FastAPI application with comprehensive endpoints
   - Automatic OpenAPI documentation
   - CORS enabled for cross-origin requests

2. **Data Models** (`src/storage/models_exact.py`)
   - SQLAlchemy models matching actual database schema
   - Optimized for String IDs and existing column structure

3. **Database** (`src/storage/database.py`)
   - SQLite database with connection pooling
   - Session management and error handling

4. **RSS Fetcher** (`src/fetcher/rss.py`)
   - Automated RSS feed processing
   - Content extraction and deduplication

5. **Content Processing** (`src/extractor/`, `src/classifier/`)
   - Article content extraction
   - ML-based classification and categorization

### 📰 News Scraping System

NewsPulse uses **RSS feed scraping** instead of traditional web scraping for reliable, efficient news collection.

#### Data Sources
- **4 Active RSS Sources**: e27, Tech in Asia, Fintech News Asia, The National
- **Regional Coverage**: Southeast Asia, Asia Pacific, Middle East
- **Disabled Source**: Arabian Business (currently disabled)

#### Scraping Process Flow
```
RSS Feeds → Async HTTP Fetch → RSS Parse → Extract Metadata → Deduplicate → Store in DB
```

#### Key Features
- **Async Processing**: Concurrent fetching with `httpx` and `asyncio`
- **Smart Deduplication**: SHA256 hashing prevents duplicate articles
- **Error Resilience**: 3 retries with exponential backoff for failed requests
- **Content Extraction**: Parses title, URL, description, author, and publish date
- **Session Tracking**: Records scraping statistics and source status

#### Technical Implementation
- **HTTP Client**: `httpx` for async HTTP requests with 30-second timeout
- **RSS Parser**: `feedparser` for reliable XML processing
- **Concurrency Control**: Semaphore limits to 3 concurrent source fetches
- **Database Storage**: SQLite with proper session and article tracking

#### What Gets Scraped
- **Article Metadata**: Title, URL, description/summary from RSS feeds
- **Publication Info**: Author (if available) and publish date
- **Source Tracking**: Associated news source and scrape timestamps
- **Content Hash**: SHA256 hash for efficient deduplication

#### How to Trigger Scraping
```bash
# Manual execution
python3 run_fetcher.py

# API trigger
POST /scrape

# Programmatic usage
from src.fetcher.rss import process_all_feeds
results = await process_all_feeds()
```

#### Current Data Statistics
- **Total Articles**: 194
- **Articles with Summaries**: 94 (48.5% quality coverage)
- **Active Sources**: 4 out of 5 configured sources
- **Regional Distribution**: Balanced across Asia-Pacific regions

### Database Schema

**Articles Table**:
- `id` (String): Unique article identifier
- `title` (String): Article title
- `link` (String): Article URL
- `summary` (Text): Article summary (HTML format)
- `content` (Text): Full article content
- `published_date` (DateTime): Publication timestamp
- `source_id` (Integer): Reference to news source
- `relevance_score` (Integer): Relevance scoring
- `primary_category` (String): Main category classification

**News Sources Table**:
- `id` (Integer): Source identifier
- `name` (String): Source name
- `rss_url` (String): RSS feed URL
- `region` (String): Geographic region
- `enabled` (Boolean): Active status

## 🔧 Recent Updates

### Summary Endpoint Implementation
- ✅ Added `/articles/{article_id}/summary` endpoint
- ✅ Returns detailed article summary by ID
- ✅ Proper error handling and validation

### Articles Filtering Enhancement
- ✅ Updated `/articles` endpoint to only return articles with summaries
- ✅ Reduced response from 194 to 94 meaningful articles
- ✅ Improved data quality and user experience

### Technical Improvements
- ✅ Fixed database schema alignment issues
- ✅ Corrected model imports and column mappings
- ✅ Enhanced error handling and logging
- ✅ Optimized query performance

## 📊 Data Quality

- **Summary Coverage**: 48.5% of articles have summaries
- **Content Sources**: 5 active regional news sources
- **Update Frequency**: Real-time RSS processing
- **Data Validation**: Comprehensive input validation and sanitization

## 🔍 API Documentation

Full interactive API documentation is available at:
- **Swagger UI**: http://127.0.0.1:8002/docs
- **ReDoc**: http://127.0.0.1:8002/redoc
- **OpenAPI Schema**: http://127.0.0.1:8002/openapi.json

## 🚀 Production Deployment

The application is containerized and ready for deployment:

```bash
# Using Docker
docker-compose up -d

# Or direct Python
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8002
```

## 📈 Performance

- **Response Time**: < 100ms for most endpoints
- **Database**: Optimized SQLite with proper indexing
- **Concurrency**: Async FastAPI with connection pooling
- **Scalability**: Ready for horizontal scaling

## 🛡 Security

- **Input Validation**: Comprehensive Pydantic models
- **SQL Injection Protection**: SQLAlchemy ORM
- **CORS Configuration**: Properly configured for cross-origin requests
- **Error Handling**: Secure error responses without sensitive data exposure

---

**NewsPulse** - Intelligent news processing for the modern web 🚀