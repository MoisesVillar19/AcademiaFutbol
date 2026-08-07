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

        ctk.CTkLabel(row, text="Día", font=ctk.CTkFont(size=10), text_color="gray").pack(side="left")
        self.combo_dia = ctk.CTkComboBox(
            row, width=55, values=[str(i).zfill(2) for i in range(1, 32)],
        )
        self.combo_dia.pack(side="left", padx=(2, 8))

        ctk.CTkLabel(row, text="Mes", font=ctk.CTkFont(size=10), text_color="gray").pack(side="left")
        meses = ["01", "02", "03", "04", "05", "06",
                 "07", "08", "09", "10", "11", "12"]
        self.combo_mes = ctk.CTkComboBox(
            row, width=55, values=meses,
        )
        self.combo_mes.pack(side="left", padx=(2, 8))

        ctk.CTkLabel(row, text="Año", font=ctk.CTkFont(size=10), text_color="gray").pack(side="left")
        anio_actual = date.today().year
        anios = [str(a) for a in range(anio_actual - 100, anio_actual + 2)]
        self.combo_anio = ctk.CTkComboBox(
            row, width=75, values=anios,
        )
        self.combo_anio.pack(side="left", padx=2)

        self._aplicar_default()

    def get(self) -> str:
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
        else:
            self.combo_dia.set("")
            self.combo_mes.set("")
            self.combo_anio.set("")

    def delete(self):
        self.combo_dia.set("")
        self.combo_mes.set("")
        self.combo_anio.set("")

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
