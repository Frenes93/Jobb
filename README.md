# Jobb 

This repository is for creating a tool to allow process engineers and project engineers work easier.

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
The root path returns a simple JSON welcome message.

## Configuration

The project currently requires no environment variables, but you can add a `.env` file to configure future features as needed.


## Testing

After installing the project dependencies, run the test suite with `pytest`:

```bash
pytest
```

This will execute the tests under the `tests/` directory and report any failures.

## Desktop Tubing Designer

A simple example desktop application using Dear PyGui is available in
`app/tubing_gui.py`. Run it with:

```bash
python app/tubing_gui.py
```


The GUI lets you choose both a system type and the fitting brand (Parker,
Butech or Swagelok). You can draw tubing lines and place valves or analyzers on
a canvas. When a new line branches off an existing one, the application
automatically inserts a tee fitting. Projects can be saved to or loaded from
JSON files.

