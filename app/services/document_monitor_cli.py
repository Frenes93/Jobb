from pathlib import Path
import sys

from .agent_tools import DocumentMonitor


def process_file(path: Path) -> None:
    try:
        text = path.read_text()
    except Exception as exc:
        print(f"Could not read {path}: {exc}")
        return
    print(f"\nAgent processed {path} -> {len(text)} characters\n")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m app.services.document_monitor_cli <file>")
        return
    doc = Path(sys.argv[1])
    monitor = DocumentMonitor(doc, process_file)
    print(f"Monitoring {doc}. Stop editing for 10 seconds to trigger agent.")
    monitor.start()


if __name__ == "__main__":
    main()
