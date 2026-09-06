import customtkinter as ctk
from controllers import auditoria_controller
from widgets.date_picker import DatePicker


class AuditoriaView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._crear_widgets()
        if hasattr(self, "tabla_frame"):
            self._cargar_logs()

    def _crear_widgets(self):
        if not auditoria_controller.puede_acceder_auditoria():
            ctk.CTkLabel(
                self, text="Acceso denegado. Solo administradores.",
                font=ctk.CTkFont(size=16), text_color="red",
            ).pack(expand=True)
            return

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            header, text="Registro de Auditoría",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            header, text="Actualizar", width=100,
            command=self._cargar_logs,
        ).pack(side="right")

        filtros = ctk.CTkFrame(self, fg_color="transparent")
        filtros.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(filtros, text="Tabla:").pack(side="left", padx=(0, 5))
        self.combo_tabla = ctk.CTkComboBox(
            filtros, values=["", "usuario", "persona", "estudiante",
                             "matricula", "cuota", "pago", "producto",
                             "venta", "egreso", "tipo_uniforme", "movimiento_inventario"],
            width=180, command=self._filtrar_por_tabla,
        )
        self.combo_tabla.set("")
        self.combo_tabla.pack(side="left", padx=5)

        self.date_picker_inicio = DatePicker(filtros, label_text="Desde:")
        self.date_picker_inicio.pack(side="left", padx=(10, 5))

        self.date_picker_fin = DatePicker(filtros, label_text="Hasta:")
        self.date_picker_fin.pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            filtros, text="Buscar", width=80,
            command=self._buscar_por_fecha,
        ).pack(side="left")

        self.tabla_frame = ctk.CTkScrollableFrame(self)
        self.tabla_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.label_status = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11))
        self.label_status.pack(pady=5)

    def _cargar_logs(self):
        for widget in self.tabla_frame.winfo_children():
            widget.destroy()

        logs = auditoria_controller.consultar_logs(limit=100)

        if not logs:
            ctk.CTkLabel(
                self.tabla_frame, text="No hay registros de auditoría",
                text_color="gray",
            ).pack(pady=20)
            return

        header_row = ctk.CTkFrame(self.tabla_frame, fg_color="#e2e8f0")
        header_row.pack(fill="x", padx=2, pady=2)

        for text, width in [("Fecha", 130), ("Usuario", 80), ("Tabla", 100),
                            ("Acción", 100), ("Registro", 70)]:
            ctk.CTkLabel(
                header_row, text=text, width=width,
                font=ctk.CTkFont(size=11, weight="bold"),
            ).pack(side="left", padx=2)

        for log in logs:
            row = ctk.CTkFrame(self.tabla_frame)
            row.pack(fill="x", padx=2, pady=1)

            ctk.CTkLabel(row, text=log.get("fecha", ""), width=130,
                         font=ctk.CTkFont(size=11)).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=str(log.get("id_usuario", "")), width=80,
                         font=ctk.CTkFont(size=11)).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=log.get("tabla_afectada", ""), width=100,
                         font=ctk.CTkFont(size=11)).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=log.get("accion", ""), width=100,
                         font=ctk.CTkFont(size=11)).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=str(log.get("id_registro", "")), width=70,
                         font=ctk.CTkFont(size=11)).pack(side="left", padx=2)

        self.label_status.configure(text=f"Mostrando {len(logs)} registro(s)")

    def _filtrar_por_tabla(self, tabla):
        for widget in self.tabla_frame.winfo_children():
            widget.destroy()

        if not tabla:
            self._cargar_logs()
            return

        logs = auditoria_controller.filtrar_por_tabla(tabla)
        self._mostrar_logs(logs)

    def _buscar_por_fecha(self):
        fecha_inicio = self.date_picker_inicio.get()
        fecha_fin = self.date_picker_fin.get()

        if not fecha_inicio or not fecha_fin:
            return

        for widget in self.tabla_frame.winfo_children():
            widget.destroy()

        logs = auditoria_controller.filtrar_por_fecha(fecha_inicio, fecha_fin)
        self._mostrar_logs(logs)

    def _mostrar_logs(self, logs):
        for widget in self.tabla_frame.winfo_children():
            widget.destroy()

        if not logs:
            ctk.CTkLabel(
                self.tabla_frame, text="No se encontraron registros",
                text_color="gray",
            ).pack(pady=20)
            return

        for log in logs:
            row = ctk.CTkFrame(self.tabla_frame)
            row.pack(fill="x", padx=2, pady=1)

            ctk.CTkLabel(row, text=log.get("fecha", ""), width=130,
                         font=ctk.CTkFont(size=11)).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=str(log.get("id_usuario", "")), width=80,
                         font=ctk.CTkFont(size=11)).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=log.get("tabla_afectada", ""), width=100,
                         font=ctk.CTkFont(size=11)).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=log.get("accion", ""), width=100,
                         font=ctk.CTkFont(size=11)).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=str(log.get("id_registro", "")), width=70,
                         font=ctk.CTkFont(size=11)).pack(side="left", padx=2)

        self.label_status.configure(text=f"Mostrando {len(logs)} registro(s)")
