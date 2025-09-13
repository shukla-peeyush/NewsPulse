# Backend Reorganization Plan

## Current Issues Identified:
1. **Multiple main files**: main.py, src/api/main*.py (4 variants)
2. **Scattered run scripts**: 6 different run_server files
3. **Empty files**: Many 0-byte files cluttering the structure
4. **Test files mixed with source code**
5. **Duplicate model files**: models.py, models_simple.py, models_exact.py
6. **No clear entry point**

## New Clean Structure:
```
BackEnd/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # Single FastAPI app entry point
│   ├── config.py                 # Configuration management
│   ├── dependencies.py           # Global dependencies
│   │
│   ├── api/                      # API routes
│   │   ├── __init__.py
│   │   ├── v1/                   # API versioning
│   │   │   ├── __init__.py
│   │   │   ├── articles.py       # Article endpoints
│   │   │   ├── sources.py        # News source endpoints
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   └── analytics.py      # Analytics endpoints
│   │   └── deps.py               # API-specific dependencies
│   │
│   ├── core/                     # Core business logic
│   │   ├── __init__.py
│   │   ├── auth.py               # Authentication logic
│   │   ├── security.py           # Security utilities
│   │   └── config.py             # Core configuration
│   │
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   ├── article.py            # Article model
│   │   ├── source.py             # News source model
│   │   ├── user.py               # User model
│   │   └── base.py               # Base model class
│   │
│   ├── schemas/                  # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── article.py            # Article schemas
│   │   ├── source.py             # Source schemas
│   │   └── user.py               # User schemas
│   │
│   ├── services/                 # Business logic services
│   │   ├── __init__.py
│   │   ├── news_fetcher.py       # RSS fetching service
│   │   ├── content_extractor.py  # Content extraction
│   │   ├── classifier.py         # ML classification
│   │   └── cache.py              # Caching service
│   │
│   ├── database/                 # Database related
│   │   ├── __init__.py
│   │   ├── connection.py         # Database connection
│   │   ├── session.py            # Session management
│   │   └── migrations/           # Alembic migrations
│   │
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       ├── logging.py            # Logging configuration
│       └── helpers.py            # Helper functions
│
├── tests/                        # All tests in separate directory
│   ├── __init__.py
│   ├── conftest.py               # Test configuration
│   ├── test_api/
│   ├── test_services/
│   └── test_models/
│
├── scripts/                      # Utility scripts
│   ├── init_db.py                # Database initialization
│   ├── run_fetcher.py            # Manual fetching
│   └── run_classifier.py         # Manual classification
│
├── data/                         # Data directory
│   └── newspulse.db              # SQLite database
│
├── requirements.txt              # Dependencies
├── alembic.ini                   # Alembic configuration
├── .env.example                  # Environment variables example
└── main.py                       # Application entry point
```

## Migration Steps:
1. Create new structure
2. Consolidate and clean up existing code
3. Move files to appropriate locations
4. Update imports and dependencies
5. Remove duplicate and empty files
6. Test the new structure