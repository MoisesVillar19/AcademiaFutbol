from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Debouncer:
    """Debounce real para Tk: cancela la llamada anterior y programa
    una nueva con target.after(wait_ms). Uso:
        self._debouncer = Debouncer(self, 300)
        entry.bind("<KeyRelease>", lambda e: self._debouncer.call(self._cargar))
    """

    target: object
    wait_ms: float
    _after_id: Any = field(default=None, repr=False)

    def call(self, fn: Callable, *args, **kwargs):
        try:
            if self._after_id is not None:
                self.target.after_cancel(self._after_id)
        except Exception:
            pass
        try:
            self._after_id = self.target.after(
                int(self.wait_ms), lambda: fn(*args, **kwargs)
            )
        except Exception:
            # Fallback sin Tk (tests): ejecución directa
            fn(*args, **kwargs)

    def cancel(self):
        try:
            if self._after_id is not None:
                self.target.after_cancel(self._after_id)
        except Exception:
            pass
        finally:
            self._after_id = None