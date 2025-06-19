# Jobb FastAPI Example

This repository contains a minimal FastAPI application. The project is intended as a starting point for building APIs and experimenting with FastAPI features.

## Installation

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application using uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```
   The service will be available at `http://127.0.0.1:8000`.

## Configuration

The project currently requires no environment variables, but a `.env` file can be placed in the repository root if you need to define settings for future features. Environment variables in this file will be loaded automatically if you integrate a tool such as `python-dotenv`.

