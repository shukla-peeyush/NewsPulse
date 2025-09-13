"""
Automated Cleanup Script for Old Backend Files
"""

import os
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cleanup_old_files():
    """Remove old messy files and directories"""
    
    # Get the BackEnd directory path
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    logger.info(f"Cleaning up old files in: {backend_dir}")
    
    # Files to remove from root
    root_files_to_remove = [
        'create_user_tables.py',
        'fix_database_path.py', 
        'fix_summary_display.py',
        'run_server_8001.py',
        'run_server_fixed.py',
        'simple_api_raw.py',
        'simple_server.py',
        'simple_server_8001.py',
        'summary_endpoint_solution.py',
        'test_api_debug.py',
        'test_articles_with_summary.py',
        'test_data_directly.py',
        'test_endpoints.py',
        'test_fixed_api.py',
        'test_summary_endpoint.py',
        'run_classifier.py',
        'run_extractor.py',
        'run_fetcher.py',
        'run_ml_classifier.py'
    ]
    
    # Remove root level files
    removed_files = 0
    for filename in root_files_to_remove:
        filepath = os.path.join(backend_dir, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.info(f"Removed: {filename}")
                removed_files += 1
            except Exception as e:
                logger.error(f"Error removing {filename}: {e}")
    
    # Backup old main.py if it exists
    old_main = os.path.join(backend_dir, 'main.py')
    backup_main = os.path.join(backend_dir, 'main_old_backup.py')
    
    if os.path.exists(old_main) and not os.path.exists(backup_main):
        try:
            # Check if it's the old main file (not our new one)
            with open(old_main, 'r') as f:
                content = f.read()
                if 'import asyncio' in content and 'feedparser' in content:
                    # This is the old main file
                    shutil.move(old_main, backup_main)
                    logger.info("Backed up old main.py to main_old_backup.py")
        except Exception as e:
            logger.error(f"Error backing up main.py: {e}")
    
    # Remove old src directory if it exists
    src_dir = os.path.join(backend_dir, 'src')
    if os.path.exists(src_dir):
        try:
            shutil.rmtree(src_dir)
            logger.info("Removed old src/ directory")
            removed_files += 1
        except Exception as e:
            logger.error(f"Error removing src/ directory: {e}")
    
    # Remove empty Python files
    for root, dirs, files in os.walk(backend_dir):
        # Skip the new app directory and venv
        if 'app' in root or 'venv' in root or 'scripts' in root or 'tests' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    if os.path.getsize(filepath) == 0:
                        os.remove(filepath)
                        logger.info(f"Removed empty file: {file}")
                        removed_files += 1
                except Exception as e:
                    logger.error(f"Error checking/removing {file}: {e}")
    
    logger.info(f"Cleanup completed! Removed {removed_files} files/directories.")
    
    # Show new structure
    print("\n" + "="*60)
    print("NEW BACKEND STRUCTURE")
    print("="*60)
    print("BackEnd/")
    print("├── app/                    # Main application package")
    print("│   ├── api/               # API routes (v1)")
    print("│   ├── core/              # Core business logic")
    print("│   ├── database/          # Database connection")
    print("│   ├── models/            # SQLAlchemy models")
    print("│   ├── schemas/           # Pydantic schemas")
    print("│   ├── services/          # Business services")
    print("│   ├── config.py          # Configuration")
    print("│   └── main.py            # FastAPI app")
    print("├── scripts/               # Utility scripts")
    print("├── tests/                 # Test files")
    print("├── data/                  # Database files")
    print("├── main.py                # Application entry point")
    print("├── requirements.txt       # Dependencies")
    print("└── .env.example           # Environment template")
    print("="*60)
    print("\nTo start the application:")
    print("1. pip install -r requirements.txt")
    print("2. python scripts/init_db.py")
    print("3. python main.py")
    print("="*60)


if __name__ == "__main__":
    cleanup_old_files()