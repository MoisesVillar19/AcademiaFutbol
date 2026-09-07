from dataclasses import dataclass
import time


@dataclass
class Debouncer:
    target: object
    wait_ms: float
    _last_call: float = 0.0

    def call(self, fn, *args, **kwargs):
        now = time.monotonic()
        elapsed = now - self._last_call
        if elapsed >= self.wait_ms / 1000:
            fn(*args, **kwargs)
            self._last_call = now
        else:
            # Reset timer; next call will execute after wait period
            self._last_call = now
            fn(*args, **kwargs)