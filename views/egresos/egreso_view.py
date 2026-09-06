import customtkinter as ctk
from tkinter import messagebox
from controllers import egreso_controller
from utils.dates import get_today


class EgresoView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._crear_widgets()
        self._cargar_egresos()

    def _crear_widgets(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        self.tab_lista = self.tabview.add("Egresos")
        self.tab_form = self.tabview.add("Registrar Egreso")
        self.tab_reporte = self.tabview.add("Reporte")
        self._crear_lista()
        self._crear_form()
        self._crear_reporte()

    def _crear_lista(self):
        header = ctk.CTkFrame(self.tab_lista, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(header, text="Egresos (Profesor/Personal/Campeonato)", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="Actualizar", width=100, command=self._cargar_egresos).pack(side="right")
        self.scroll = ctk.CTkScrollableFrame(self.tab_lista)
        self.scroll.pack(fill="both", expand=True, padx=5, pady=5)

    def _crear_form(self):
        scroll = ctk.CTkScrollableFrame(self.tab_form)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(scroll, text="Registrar Egreso", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0,10))
        ctk.CTkLabel(scroll, text="Concepto *").pack(anchor="w")
        self.combo_concepto = ctk.CTkComboBox(scroll, width=250, values=["PROFESOR","PERSONAL","CAMPEONATO_FIJO","ARBITRAJE","VIATICOS"])
        self.combo_concepto.set("PROFESOR")
        self.combo_concepto.pack(anchor="w", pady=3)
        ctk.CTkLabel(scroll, text="Monto S/ *").pack(anchor="w")
        self.entry_monto = ctk.CTkEntry(scroll, width=150, placeholder_text="200")
        self.entry_monto.pack(anchor="w", pady=3)
        ctk.CTkLabel(scroll, text="Fecha *").pack(anchor="w")
        self.entry_fecha = ctk.CTkEntry(scroll, width=150)
        self.entry_fecha.insert(0, get_today())
        self.entry_fecha.pack(anchor="w", pady=3)
        ctk.CTkLabel(scroll, text="Responsable").pack(anchor="w")
        self.entry_resp = ctk.CTkEntry(scroll, width=300, placeholder_text="Nombre")
        self.entry_resp.pack(anchor="w", pady=3)
        ctk.CTkLabel(scroll, text="Observación").pack(anchor="w")
        self.entry_obs = ctk.CTkEntry(scroll, width=400)
        self.entry_obs.pack(anchor="w", pady=3)
        self.label_status = ctk.CTkLabel(scroll, text="")
        self.label_status.pack(anchor="w", pady=5)
        ctk.CTkButton(scroll, text="Guardar", width=120, command=self._guardar).pack(anchor="w", pady=10)

    def _crear_reporte(self):
        frame = ctk.CTkFrame(self.tab_reporte, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(frame, text="Ingresos vs Egresos (mes actual)", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.label_reporte = ctk.CTkLabel(frame, text="", justify="left")
        self.label_reporte.pack(anchor="w", pady=5)
        ctk.CTkButton(frame, text="Calcular", command=self._calcular).pack(anchor="w", pady=5)

    def _cargar_egresos(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        egresos = egreso_controller.listar_egresos()
        if not egresos:
            ctk.CTkLabel(self.scroll, text="No hay egresos", text_color="gray").pack(pady=20)
            return
        for e in egresos:
            card = ctk.CTkFrame(self.scroll)
            card.pack(fill="x", padx=5, pady=3)
            ctk.CTkLabel(card, text=f"{e['concepto']} - S/{e['monto']:.2f} - {e['fecha']}", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=10, pady=3)
            ctk.CTkLabel(card, text=f"Resp: {e.get('responsable','')} | {e.get('observacion','')}", text_color="gray").pack(anchor="w", padx=10)

    def _guardar(self):
        data = {
            "concepto": self.combo_concepto.get(),
            "monto": self.entry_monto.get().strip(),
            "fecha": self.entry_fecha.get().strip(),
            "responsable": self.entry_resp.get().strip(),
            "observacion": self.entry_obs.get().strip(),
        }
        exito, msg, _ = egreso_controller.registrar_egreso(data)
        self.label_status.configure(text=msg, text_color="green" if exito else "red")
        if exito:
            self._cargar_egresos()
            self.entry_monto.delete(0, "end")

    def _calcular(self):
        from datetime import date
        hoy = date.today()
        ini = hoy.replace(day=1).isoformat()
        fin = hoy.isoformat()
        rep = egreso_controller.reporte_ingresos_vs_egresos(ini, fin)
        if rep:
            self.label_reporte.configure(text=f"Ingresos: S/{rep.get('total_ingresos',0):.2f} (ventas {rep.get('ingresos_ventas',0):.2f} + pagos {rep.get('ingresos_pagos',0):.2f})\nEgresos: S/{rep.get('egresos',0):.2f}\nNeto: S/{rep.get('neto',0):.2f}")
