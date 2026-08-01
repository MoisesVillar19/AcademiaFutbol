import customtkinter as ctk
from tkinter import filedialog, messagebox
from controllers import reporte_controller
from utils.dates import get_today


class ReporteView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._crear_widgets()

    def _crear_widgets(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            header, text="Reportes",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(side="left")

        self.contenido = ctk.CTkScrollableFrame(self)
        self.contenido.pack(fill="both", expand=True, padx=15, pady=5)

        self._mostrar_lista_reportes()

    def _mostrar_lista_reportes(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()

        reportes = reporte_controller.listar_reportes()

        for reporte in reportes:
            card = ctk.CTkFrame(self.contenido)
            card.pack(fill="x", padx=5, pady=5)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)

            ctk.CTkLabel(
                info_frame, text=reporte["nombre"],
                font=ctk.CTkFont(size=16, weight="bold"),
            ).pack(anchor="w")

            ctk.CTkLabel(
                info_frame, text=reporte["descripcion"],
                font=ctk.CTkFont(size=12), text_color="gray",
            ).pack(anchor="w")

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=10, pady=10)

            ctk.CTkButton(
                btn_frame, text="Exportar Excel", width=120,
                command=lambda r=reporte["id"], n=reporte["nombre"]: self._exportar(r, n),
            ).pack(side="right")

    def _exportar(self, reporte_id, nombre_reporte):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Exportar: {nombre_reporte}")
        dialog.geometry("400x280")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="Seleccionar Período del Reporte",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(20, 10))

        fecha_actual = get_today()
        mes_actual = fecha_actual[:7]

        ctk.CTkLabel(dialog, text="Fecha Inicio (YYYY-MM-DD):").pack(pady=(10, 5))
        entry_inicio = ctk.CTkEntry(dialog, width=280)
        entry_inicio.insert(0, f"{mes_actual}-01")
        entry_inicio.pack()

        ctk.CTkLabel(dialog, text="Fecha Fin (YYYY-MM-DD):").pack(pady=(10, 5))
        entry_fin = ctk.CTkEntry(dialog, width=280)
        entry_fin.insert(0, fecha_actual)
        entry_fin.pack()

        resultado = {"valor": None}

        def confirmar():
            fecha_inicio = entry_inicio.get().strip()
            fecha_fin = entry_fin.get().strip()

            if not fecha_inicio or not fecha_fin:
                messagebox.showwarning("Advertencia", "Ingrese ambas fechas")
                return

            ruta = filedialog.asksaveasfilename(
                title="Guardar reporte",
                defaultextension=".xlsx",
                filetypes=[("Archivos Excel", "*.xlsx")],
                initialfile=f"reporte_{reporte_id}_{fecha_inicio}_a_{fecha_fin}.xlsx",
            )

            if not ruta:
                return

            resultado["valor"] = (fecha_inicio, fecha_fin, ruta)
            dialog.destroy()

        ctk.CTkButton(
            dialog, text="Seleccionar y Exportar", width=200,
            command=confirmar,
        ).pack(pady=20)

        dialog.wait_window()

        if resultado["valor"]:
            fecha_inicio, fecha_fin, ruta = resultado["valor"]
            self._ejecutar_exportacion(reporte_id, fecha_inicio, fecha_fin, ruta)

    def _ejecutar_exportacion(self, reporte_id, fecha_inicio, fecha_fin, ruta):
        try:
            if reporte_id == "morosos":
                exito, msg = reporte_controller.reporte_morosos(ruta)
            elif reporte_id == "pagos_fecha":
                exito, msg = reporte_controller.reporte_pagos_por_fecha(
                    fecha_inicio, fecha_fin, ruta
                )
            elif reporte_id == "ingresos_mensuales":
                exito, msg = reporte_controller.reporte_ingresos_mensuales(ruta)
            elif reporte_id == "alumnos_categoria":
                exito, msg = reporte_controller.reporte_alumnos_por_categoria(ruta)
            elif reporte_id == "inventario":
                exito, msg = reporte_controller.reporte_inventario(ruta)
            elif reporte_id == "becas_activas":
                exito, msg = reporte_controller.reporte_becas_activas(ruta)
            else:
                messagebox.showerror("Error", "Reporte no reconocido")
                return

            if exito:
                messagebox.showinfo("Éxito", msg)
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
