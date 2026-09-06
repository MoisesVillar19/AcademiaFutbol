import os
import customtkinter as ctk
from tkinter import messagebox, filedialog
from controllers import egreso_controller
from utils.dates import get_today
from utils.constants import COMPROBANTES_DIR
try:
    from PIL import Image
except ImportError:
    Image = None


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
        ctk.CTkLabel(scroll, text="Comprobante (opcional, jpg/png/pdf ≤5MB)").pack(anchor="w", pady=(5,0))
        comp_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        comp_frame.pack(fill="x", anchor="w", pady=2)
        self.btn_comp = ctk.CTkButton(comp_frame, text="📎 Seleccionar comprobante", width=180, command=self._elegir_comprobante)
        self.btn_comp.pack(side="left", padx=5)
        self.label_comp = ctk.CTkLabel(comp_frame, text="Sin comprobante", text_color="gray")
        self.label_comp.pack(side="left", padx=5)
        self.label_comp_preview = ctk.CTkLabel(comp_frame, text="")
        self.label_comp_preview.pack(side="left", padx=5)
        self._comprobante_path = None
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
            card = ctk.CTkFrame(self.scroll, border_width=1, border_color="#E5E7EB", corner_radius=8)
            card.pack(fill="x", padx=5, pady=3)
            ctk.CTkLabel(card, text=f"{e['concepto']} - S/{e['monto']:.2f} - {e['fecha']}", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=10, pady=3)
            ctk.CTkLabel(card, text=f"Resp: {e.get('responsable','')} | {e.get('observacion','')}", text_color="gray").pack(anchor="w", padx=10)
            comp = e.get("comprobante_path")
            if comp and os.path.isfile(comp) and Image:
                try:
                    img = Image.open(comp)
                    img.thumbnail((60, 60))
                    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(60, 60))
                    if not hasattr(self, "_comp_cache"):
                        self._comp_cache = {}
                    self._comp_cache[e["id_egreso"]] = ctk_img
                    lbl = ctk.CTkLabel(card, image=ctk_img, text="")
                    lbl.pack(anchor="w", padx=10, pady=2)
                    lbl.bind("<Button-1>", lambda ev, p=comp: os.startfile(p) if os.path.exists(p) else None)
                    ctk.CTkLabel(card, text=f"📎 {os.path.basename(comp)} (clic para ampliar)", font=ctk.CTkFont(size=11), text_color="#7C3AED").pack(anchor="w", padx=10)
                except Exception:
                    ctk.CTkLabel(card, text=f"📎 {os.path.basename(comp)}", font=ctk.CTkFont(size=11), text_color="#7C3AED").pack(anchor="w", padx=10)
            elif comp:
                ctk.CTkLabel(card, text=f"📎 {os.path.basename(comp)}", font=ctk.CTkFont(size=11), text_color="#7C3AED").pack(anchor="w", padx=10)

    def _elegir_comprobante(self):
        path = filedialog.askopenfilename(filetypes=[("Imagen/PDF","*.jpg *.jpeg *.png *.pdf"),("Todos","*.*")])
        if not path:
            return
        if os.path.getsize(path) > 5 * 1024 * 1024:
            self.label_status.configure(text="❌ Comprobante debe ser ≤5MB", text_color="red")
            return
        os.makedirs(COMPROBANTES_DIR, exist_ok=True)
        # copiar a OneDrive con nombre temporal, se renombrará al guardar con recibo
        self._comprobante_path = path
        self.label_comp.configure(text=f"✅ {os.path.basename(path)}")
        if Image and path.lower().endswith(('.jpg','.jpeg','.png')) and os.path.isfile(path):
            try:
                img = Image.open(path)
                img.thumbnail((60, 60))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(60, 60))
                self._comp_preview = ctk_img
                self.label_comp_preview.configure(image=ctk_img, text="")
            except Exception:
                pass

    def _guardar(self):
        comprobante_dest = None
        if self._comprobante_path:
            try:
                os.makedirs(COMPROBANTES_DIR, exist_ok=True)
                # se copiara con nombre EG- id tras insert, por ahora guardar tmp
                comprobante_dest = self._comprobante_path
            except Exception:
                comprobante_dest = self._comprobante_path
        data = {
            "concepto": self.combo_concepto.get(),
            "monto": self.entry_monto.get().strip(),
            "fecha": self.entry_fecha.get().strip(),
            "responsable": self.entry_resp.get().strip(),
            "observacion": self.entry_obs.get().strip(),
            "comprobante_path": comprobante_dest,
        }
        exito, msg, id_eg = egreso_controller.registrar_egreso(data)
        self.label_status.configure(text=msg, text_color="green" if exito else "red")
        if exito:
            # si hay comprobante, copiar con nombre EG-{id}.jpg
            if self._comprobante_path and id_eg:
                try:
                    ext = os.path.splitext(self._comprobante_path)[1] or ".jpg"
                    dest = os.path.join(COMPROBANTES_DIR, f"EG-{id_eg}{ext}")
                    import shutil
                    shutil.copy2(self._comprobante_path, dest)
                    # actualizar registro con path final
                    from database.connection import get_connection
                    conn = get_connection()
                    conn.execute("UPDATE egreso SET comprobante_path=? WHERE id_egreso=?", (dest, id_eg))
                    conn.commit()
                except Exception:
                    pass
            self._comprobante_path = None
            self.label_comp.configure(text="Sin comprobante")
            self.label_comp_preview.configure(image=None, text="")
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
