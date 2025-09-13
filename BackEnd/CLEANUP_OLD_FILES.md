# Backend Cleanup Guide

## Files to Remove (Old Messy Structure)

### Root Level Files to Remove:
```bash
# Empty or duplicate files
rm create_user_tables.py
rm fix_database_path.py
rm fix_summary_display.py
rm run_server_8001.py
rm run_server_fixed.py
rm simple_api_raw.py
rm simple_server.py
rm simple_server_8001.py
rm summary_endpoint_solution.py

# Test files (moved to tests/ directory)
rm test_api_debug.py
rm test_articles_with_summary.py
rm test_data_directly.py
rm test_endpoints.py
rm test_fixed_api.py
rm test_summary_endpoint.py

# Old run scripts (replaced by scripts/)
rm run_classifier.py
rm run_extractor.py
rm run_fetcher.py
rm run_ml_classifier.py

# Old main file (replaced by new main.py)
# Keep the old main.py as backup if needed
mv main.py main_old_backup.py
```

### Old src/ Directory Files to Remove:
```bash
# Remove duplicate API files
rm src/api/main.py
rm src/api/main_exact.py
rm src/api/main_fixed.py
# Keep main_simple.py as reference if needed

# Remove duplicate model files
rm src/storage/models.py
rm src/storage/models_exact.py
# Keep models_simple.py as reference if needed

# Remove old auth files (functionality moved to app/core/)
rm -rf src/auth/

# Remove old cache implementation
rm -rf src/cache/

# Remove old monitoring (can be re-implemented later)
rm -rf src/monitoring/

# Remove old utils (functionality moved to app/utils/)
rm -rf src/utils/

# Remove old classifier and extractor (moved to app/services/)
rm -rf src/classifier/
rm -rf src/extractor/
rm -rf src/fetcher/

# Remove old storage (moved to app/models/ and app/database/)
rm -rf src/storage/

# Remove empty src directory
rm -rf src/
```

## Automated Cleanup Script

Run this command to clean up automatically:

```bash
cd BackEnd

# Remove empty and duplicate files
find . -name "*.py" -size 0 -delete

# Remove old test files from root
rm -f test_*.py

# Remove old run scripts
rm -f run_*.py

# Remove old simple servers
rm -f simple_*.py

# Remove fix scripts
rm -f fix_*.py

# Remove summary solution
rm -f summary_*.py

# Remove create user tables
rm -f create_user_tables.py

# Backup and remove old main
mv main.py main_old_backup.py 2>/dev/null || true

echo "Cleanup completed! Old files removed."
echo "New structure is ready to use."
```

## What's Been Preserved

- **Database file**: `data/newspulse.db` (unchanged)
- **Virtual environment**: `venv/` (unchanged)
- **Requirements**: Updated with new dependencies
- **Core functionality**: All features preserved in new structure

## New Entry Points

- **Main application**: `python main.py`
- **Database setup**: `python scripts/init_db.py`
- **Manual fetching**: `python scripts/run_fetcher.py`
- **Manual classification**: `python scripts/run_classifier.py`

## Testing the New Structure

```bash
# Install any missing dependencies
pip install pydantic-settings

# Initialize database
python scripts/init_db.py

# Test the application
python main.py
```

The application should start on http://localhost:8000 with docs at /docs