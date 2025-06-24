import os, sys; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import time
from pathlib import Path
from app.services.agent_tools import DocumentMonitor, ChatAgent


def test_document_monitor_triggers(tmp_path):
    doc = tmp_path / "file.txt"
    doc.write_text("hello")
    triggered = []

    def callback(path: Path) -> None:
        triggered.append(path.read_text())

    monitor = DocumentMonitor(doc, callback, delay=0.1)
    monitor.check()  # initial state
    doc.write_text("changed")
    monitor.check()
    time.sleep(0.2)
    assert triggered == ["changed"]


def test_chat_agent_response():
    outputs = []
    agent = ChatAgent(response_fn=lambda msg: msg.upper(), delay=0.1)
    agent.user_message("hi")
    time.sleep(0.2)
    assert agent.history[-1] == ("agent", "HI")
