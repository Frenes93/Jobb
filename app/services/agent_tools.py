import threading
import time
from pathlib import Path
from typing import Callable, List, Tuple


class DocumentMonitor:
    """Monitor a file and trigger a callback after a period of inactivity."""

    def __init__(self, path: str | Path, callback: Callable[[Path], None], delay: float = 10.0) -> None:
        self.path = Path(path)
        self.callback = callback
        self.delay = delay
        if self.path.exists():
            stat = self.path.stat()
            self._last_state: tuple[float, int] = (stat.st_mtime, stat.st_size)
        else:
            self._last_state = (None, 0)
        self._timer: threading.Timer | None = None

    def _on_idle(self) -> None:
        self._timer = None
        self.callback(self.path)

    def check(self) -> None:
        """Check the file for modifications and reset the idle timer."""
        if self.path.exists():
            stat = self.path.stat()
            state = (stat.st_mtime, stat.st_size)
        else:
            state = (None, 0)
        if state != self._last_state:
            self._last_state = state
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.delay, self._on_idle)
            self._timer.start()

    def start(self, poll_interval: float = 1.0) -> None:
        """Continuously monitor the file until interrupted."""
        try:
            while True:
                self.check()
                time.sleep(poll_interval)
        except KeyboardInterrupt:
            pass
        finally:
            if self._timer:
                self._timer.cancel()


class ChatAgent:
    """Simple chat agent that responds after a period of inactivity."""

    def __init__(self, response_fn: Callable[[str], str] | None = None, delay: float = 10.0) -> None:
        self.response_fn = response_fn or (lambda msg: msg[::-1])
        self.delay = delay
        self.history: List[Tuple[str, str]] = []
        self._timer: threading.Timer | None = None

    def _respond(self) -> None:
        if not self.history:
            return
        last_msg = self.history[-1][1]
        reply = self.response_fn(last_msg)
        self.history.append(("agent", reply))
        print(f"Agent: {reply}")
        self._timer = None

    def user_message(self, message: str) -> None:
        self.history.append(("user", message))
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(self.delay, self._respond)
        self._timer.start()
