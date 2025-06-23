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
pipes, valves, pumps, filters and analysers onto a canvas and draw lines between
them. The application automatically inserts tees when lines intersect, adds
bulkheads when a line enters or exits the dashed frame, and suggests adapters if
line sizes differ. A drop-down lets you pick the fitting brand (Parker, Butech
or Swagelok) used in the handleliste. The previous API welcome message has
moved to `http://127.0.0.1:8000/api`. The interactive API docs are still
available at `http://127.0.0.1:8000/docs`. There is also a **Reset** button to
clear the diagram and start over.
`http://127.0.0.1:8000/api`. The interactive API docs are still available at
`http://127.0.0.1:8000/docs`.

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

The GUI lets you choose a system type, draw tubing lines and place valves or
analyzers on a canvas. Projects can be saved to or loaded from JSON files.
