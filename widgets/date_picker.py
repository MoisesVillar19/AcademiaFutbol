"""Selector de fecha priorizando ESCRITURA (los combos eran rudimentarios).

Uso: escribir libre (AAAA-MM-DD, DD/MM/AAAA, DD-MM-AAAA o 8 dígitos),
Enter o salir del campo normaliza. Botón Hoy. API compatible: get/set/delete.
"""
import customtkinter as ctk
from datetime import date


BORDE_OK = "#22C55E"
BORDE_MAL = "#DC2626"
BORDE_NEUTRO = "#E5E7EB"


def parsear_fecha(texto: str | None) -> str | None:
    """Normaliza a YYYY-MM-DD o None si inválido/vacío.

    Acepta: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY y 8 dígitos
    (DDMMYYYY, o YYYYMMDD si empieza en 19/20 con mes válido).
    """
    if not texto:
        return None
    t = texto.strip()
    if not t:
        return None
    # datetime con hora ("2020-05-10 14:30:00" / "...T..."): usar fecha
    if len(t) > 10 and t[10] in (" ", "T") and len(t) >= 10:
        t = t[:10]
    try:
        a = m = d = None
        if len(t) == 10 and t[4] == "-" and t[7] == "-":
            a, m, d = t.split("-")
        elif len(t) == 10 and t[4] == "/" and t[7] == "/":
            a, m, d = t.split("/")
        elif len(t) == 10 and t[2] in "/-." and t[5] in "/-.":
            d, m, a = t[:2], t[3:5], t[6:10]
        elif len(t) == 8 and t.isdigit():
            if t[:2] in ("19", "20") and 1 <= int(t[4:6]) <= 12:
                a, m, d = t[:4], t[4:6], t[6:8]
            else:
                d, m, a = t[:2], t[2:4], t[4:8]
        else:
            return None
        anio, mes, dia = int(a), int(m), int(d)
        fecha = date(anio, mes, dia)  # valida calendario real (no 30-feb)
        if not (1900 <= anio <= 2100):
            return None
        return fecha.strftime("%Y-%m-%d")
    except (ValueError, TypeError, IndexError):
        return None


class DatePicker(ctk.CTkFrame):
    def __init__(self, parent, label_text="", width=300, default=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._label_text = label_text
        self._width = width
        self._default = default
        self._crear_widgets()

    def _crear_widgets(self):
        if self._label_text:
            ctk.CTkLabel(
                self, text=self._label_text,
                font=ctk.CTkFont(size=12),
            ).pack(anchor="w", pady=(0, 3))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(anchor="w")

        self.entry_fecha = ctk.CTkEntry(
            row, width=130, placeholder_text="AAAA-MM-DD",
            border_color=BORDE_NEUTRO,
        )
        self.entry_fecha.pack(side="left", padx=(0, 6))
        self.entry_fecha.bind("<KeyRelease>", self._on_escribir)
        self.entry_fecha.bind("<FocusOut>", self._on_normalizar)
        self.entry_fecha.bind("<Return>", self._on_normalizar)

        ctk.CTkButton(row, text="Hoy", width=56, height=28,
                      command=self._set_hoy).pack(side="left", padx=2)
        ctk.CTkLabel(row, text="✏️ escribe: 2026-09-06 o 06/09/2026",
                     font=ctk.CTkFont(size=10), text_color="gray").pack(side="left", padx=6)

        self._aplicar_default()

    def _on_escribir(self, event=None):
        val = self.entry_fecha.get()
        if not val.strip():
            self._pintar_borde(BORDE_NEUTRO)
            return
        ok = parsear_fecha(val) is not None
        # mientras escribe (corto) no marcar rojo todavía
        if ok:
            self._pintar_borde(BORDE_OK)
        elif len(val.strip()) >= 8:
            self._pintar_borde(BORDE_MAL)
        else:
            self._pintar_borde(BORDE_NEUTRO)

    def _on_normalizar(self, event=None):
        val = self.entry_fecha.get().strip()
        if not val:
            self._pintar_borde(BORDE_NEUTRO)
            return
        norm = parsear_fecha(val)
        if norm:
            self.entry_fecha.delete(0, "end")
            self.entry_fecha.insert(0, norm)
            self._pintar_borde(BORDE_OK)
        else:
            self._pintar_borde(BORDE_MAL)

    def _pintar_borde(self, color):
        try:
            self.entry_fecha.configure(border_color=color)
        except Exception:
            pass

    def _set_hoy(self):
        self.set(date.today().strftime("%Y-%m-%d"))

    def es_valido(self) -> bool:
        val = self.entry_fecha.get().strip()
        return not val or parsear_fecha(val) is not None

    def get(self) -> str:
        norm = parsear_fecha(self.entry_fecha.get())
        return norm or ""

    def set(self, fecha: str):
        norm = parsear_fecha(fecha)
        self.entry_fecha.delete(0, "end")
        if norm:
            self.entry_fecha.insert(0, norm)
            self._pintar_borde(BORDE_OK)
        else:
            self._pintar_borde(BORDE_NEUTRO)

    def delete(self):
        self.entry_fecha.delete(0, "end")
        self._pintar_borde(BORDE_NEUTRO)

    def _aplicar_default(self):
        hoy = date.today()
        if self._default == "today":
            self.set(hoy.strftime("%Y-%m-%d"))
        elif self._default == "start_of_month":
            self.set(hoy.strftime("%Y-%m-01"))
        elif self._default == "start_of_year":
            self.set(hoy.strftime("%Y-01-01"))
        else:
            self.delete()
