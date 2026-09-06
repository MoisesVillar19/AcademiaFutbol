import customtkinter as ctk
from datetime import date


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

        # Entrada libre + combos clickables (escribir o clickear)
        ctk.CTkLabel(row, text="Fecha (YYYY-MM-DD):", font=ctk.CTkFont(size=10), text_color="gray").pack(side="left", padx=(0,5))
        self.entry_fecha = ctk.CTkEntry(row, width=120, placeholder_text="2026-09-06")
        self.entry_fecha.pack(side="left", padx=(0, 8))
        self.entry_fecha.bind("<KeyRelease>", self._on_entry_change)
        self.entry_fecha.bind("<FocusOut>", self._on_entry_change)

        ctk.CTkLabel(row, text="o", font=ctk.CTkFont(size=10), text_color="gray").pack(side="left", padx=2)

        ctk.CTkLabel(row, text="Día", font=ctk.CTkFont(size=10), text_color="gray").pack(side="left")
        self.combo_dia = ctk.CTkComboBox(
            row, width=55, values=[str(i).zfill(2) for i in range(1, 32)], command=lambda v: self._sync_from_combos()
        )
        self.combo_dia.pack(side="left", padx=(2, 8))

        ctk.CTkLabel(row, text="Mes", font=ctk.CTkFont(size=10), text_color="gray").pack(side="left")
        meses = ["01", "02", "03", "04", "05", "06",
                 "07", "08", "09", "10", "11", "12"]
        self.combo_mes = ctk.CTkComboBox(
            row, width=55, values=meses, command=lambda v: self._sync_from_combos()
        )
        self.combo_mes.pack(side="left", padx=(2, 8))

        ctk.CTkLabel(row, text="Año", font=ctk.CTkFont(size=10), text_color="gray").pack(side="left")
        anio_actual = date.today().year
        anios = [str(a) for a in range(anio_actual - 100, anio_actual + 2)]
        self.combo_anio = ctk.CTkComboBox(
            row, width=75, values=anios, command=lambda v: self._sync_from_combos()
        )
        self.combo_anio.pack(side="left", padx=2)

        ctk.CTkButton(row, text="Hoy", width=50, height=28, command=self._set_hoy).pack(side="left", padx=5)

        self._aplicar_default()

    def _sync_from_combos(self):
        # combos → entry
        dia = self.combo_dia.get().strip()
        mes = self.combo_mes.get().strip()
        anio = self.combo_anio.get().strip()
        if dia and mes and anio:
            self.entry_fecha.delete(0, "end")
            self.entry_fecha.insert(0, f"{anio}-{mes}-{dia}")

    def _on_entry_change(self, event=None):
        # entry → combos
        val = self.entry_fecha.get().strip()
        if len(val) >= 10 and val[4] == "-" and val[7] == "-":
            try:
                a,m,d = val[:10].split("-")
                if a.isdigit() and m.isdigit() and d.isdigit():
                    self.combo_anio.set(a)
                    self.combo_mes.set(m.zfill(2))
                    self.combo_dia.set(d.zfill(2))
            except Exception:
                pass

    def _set_hoy(self):
        self.set(date.today().strftime("%Y-%m-%d"))

    def get(self) -> str:
        # prioriza entry si está completo
        val = self.entry_fecha.get().strip()
        if len(val) >= 10:
            # valida quick
            try:
                a,m,d = val[:10].split("-")
                int(a); int(m); int(d)
                return f"{a.zfill(4)}-{m.zfill(2)}-{d.zfill(2)}"
            except Exception:
                pass
        # fallback combos
        dia = self.combo_dia.get().strip()
        mes = self.combo_mes.get().strip()
        anio = self.combo_anio.get().strip()
        if dia and mes and anio:
            return f"{anio}-{mes}-{dia}"
        return ""

    def set(self, fecha: str):
        if fecha and len(fecha) >= 10:
            partes = fecha[:10].split("-")
            if len(partes) == 3:
                self.combo_anio.set(partes[0])
                self.combo_mes.set(partes[1])
                self.combo_dia.set(partes[2])
                self.entry_fecha.delete(0, "end")
                self.entry_fecha.insert(0, f"{partes[0]}-{partes[1]}-{partes[2]}")
        else:
            self.combo_dia.set("")
            self.combo_mes.set("")
            self.combo_anio.set("")
            self.entry_fecha.delete(0, "end")

    def delete(self):
        self.combo_dia.set("")
        self.combo_mes.set("")
        self.combo_anio.set("")
        self.entry_fecha.delete(0, "end")

    def _aplicar_default(self):
        hoy = date.today()
        if self._default == "today":
            self.set(hoy.strftime("%Y-%m-%d"))
        elif self._default == "start_of_month":
            self.set(hoy.strftime("%Y-%m-01"))
        elif self._default == "start_of_year":
            self.set(hoy.strftime("%Y-01-01"))
        else:
            self.combo_dia.set("")
            self.combo_mes.set("")
            self.combo_anio.set("")
            self.entry_fecha.delete(0, "end")
