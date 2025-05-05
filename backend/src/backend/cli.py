"""
CLI utility for the Agentic backend.
"""
import argparse
import logging
import sys
import os
from pathlib import Path

from backend.core.config import settings
from backend.db.database import Base, engine
from backend.main import start as start_app


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def init_db():
    """Initialize database."""
    Base.metadata.create_all(bind=engine)
    logging.info("Database tables created.")


def main():
    """Execute CLI command."""
    parser = argparse.ArgumentParser(description="Agentic Backend CLI")
    parser.add_argument("--init-db", action="store_true", help="Initialize database")
    parser.add_argument("--run", action="store_true", help="Run application")
    
    args = parser.parse_args()
    
    setup_logging()
    
    if args.init_db:
        init_db()
    
    if args.run:
        start_app()
    
    if not any([args.init_db, args.run]):
        parser.print_help()


if __name__ == "__main__":
    main()