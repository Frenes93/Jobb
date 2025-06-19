# Jobb FastAPI Example

This repository contains a minimal FastAPI application. The project is intended as a starting point for building APIs and experimenting with FastAPI features.

## Installation

1. Install the dependencies listed in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   This project only requires `fastapi`, `uvicorn`, `pydantic`, and `httpx`.
2. Run the application using uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```
   The service will be available at `http://127.0.0.1:8000`.
   Visiting the root URL now launches a small web UI for creating a P&ID
   drawing in the browser. The application automatically determines the Parker
   fittings required between components and outputs a complete handleliste.
   The previous API welcome message has moved to `http://127.0.0.1:8000/api`.
   The interactive API docs are still available at `http://127.0.0.1:8000/docs`.

## Configuration

The project currently requires no environment variables, but you can add a `.env` file to configure future features as needed.


## Testing

After installing the project dependencies, run the test suite with `pytest`:

```bash
pytest
```

This will execute the tests under the `tests/` directory and report any failures.
