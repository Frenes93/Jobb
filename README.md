# Jobb FastAPI Example

This repository contains a minimal FastAPI application. The project is intended as a starting point for building APIs and experimenting with FastAPI features.

## Installation

1. Install the dependencies listed in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   The file now includes packages for working with databases
   (`SQLAlchemy`, `psycopg2-binary`), generating CSV/Excel files
   (`pandas`, `openpyxl`), creating PDF reports (`reportlab`), and
   interfacing with offline models via `ollama`.
2. Run the application using uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```
   The service will be available at `http://127.0.0.1:8000`.
3. Alternatively start the app directly:
   ```bash
   python app/main.py
   ```

## Configuration

The project currently requires no environment variables, but a `.env` file can be placed in the repository root if you need to define settings for future features. Environment variables in this file will be loaded automatically if you integrate a tool such as `python-dotenv`.

