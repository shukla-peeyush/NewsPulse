"""
Script to run RSS fetcher
"""

import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.fetcher.main import main

if __name__ == "__main__":
    main()