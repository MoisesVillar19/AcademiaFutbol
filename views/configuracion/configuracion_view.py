import customtkinter as ctk
from tkinter import messagebox
from controllers import configuracion_controller


class ConfiguracionView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._crear_widgets()
        self._cargar_configuracion()

    def _crear_widgets(self):
        if not configuracion_controller.puede_acceder():
            ctk.CTkLabel(
                self, text="Acceso denegado. Solo administradores.",
                font=ctk.CTkFont(size=16), text_color="red",
            ).pack(expand=True)
            return

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            header, text="Configuración del Sistema",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(side="left")

        self.contenido = ctk.CTkScrollableFrame(self)
        self.contenido.pack(fill="both", expand=True, padx=15, pady=5)

    def _cargar_configuracion(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()

        config = configuracion_controller.obtener_configuracion()
        if not config:
            ctk.CTkLabel(
                self.contenido, text="Error: No se pudo cargar la configuración",
                text_color="red",
            ).pack(pady=20)
            return

        self.entries = {}

        general_frame = ctk.CTkFrame(self.contenido)
        general_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            general_frame, text="General",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self._crear_campo(general_frame, "nombre_academia", "Nombre de la Academia",
                          config.get("nombre_academia", ""))
        self._crear_campo(general_frame, "direccion", "Dirección",
                          config.get("direccion", ""))
        self._crear_campo(general_frame, "telefono", "Teléfono",
                          config.get("telefono", ""))
        self._crear_campo(general_frame, "correo", "Correo",
                          config.get("correo", ""))

        mora_frame = ctk.CTkFrame(self.contenido)
        mora_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            mora_frame, text="Mora",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.mora_switch = ctk.CTkSwitch(
            mora_frame, text="Habilitar Mora",
        )
        self.mora_switch.pack(anchor="w", padx=10, pady=5)
        if config.get("mora_habilitada", 0):
            self.mora_switch.select()

        self._crear_campo(mora_frame, "porcentaje_mora", "Porcentaje de Mora (%)",
                          str(config.get("porcentaje_mora", 0)))

        vencimiento_frame = ctk.CTkFrame(self.contenido)
        vencimiento_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            vencimiento_frame, text="Vencimiento y Cuotas",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self._crear_campo(vencimiento_frame, "dias_por_vencer", "Días por Vencer",
                          str(config.get("dias_por_vencer", 3)))

        self.becas_switch = ctk.CTkSwitch(
            vencimiento_frame, text="Permitir Múltiples Becas",
        )
        self.becas_switch.pack(anchor="w", padx=10, pady=5)
        if config.get("permitir_multiples_becas", 1):
            self.becas_switch.select()

        backup_frame = ctk.CTkFrame(self.contenido)
        backup_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            backup_frame, text="Backup",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.backup_switch = ctk.CTkSwitch(
            backup_frame, text="Backup Automático",
        )
        self.backup_switch.pack(anchor="w", padx=10, pady=5)
        if config.get("backup_automatico", 1):
            self.backup_switch.select()

        self._crear_campo(backup_frame, "frecuencia_backup", "Frecuencia (días)",
                          str(config.get("frecuencia_backup", 7)))
        self._crear_campo(backup_frame, "ruta_backup", "Ruta de Backup",
                          config.get("ruta_backup", "backups/"))
        self._crear_campo(backup_frame, "correo_onedrive", "Correo OneDrive",
                          config.get("correo_onedrive", ""))

        btn_frame = ctk.CTkFrame(self.contenido, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=10)

        ctk.CTkButton(
            btn_frame, text="Guardar Cambios", width=150,
            command=self._guardar,
        ).pack(side="right")

    def _crear_campo(self, parent, key, label, valor):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=2)

        ctk.CTkLabel(frame, text=label, width=180, anchor="w").pack(side="left")

        entry = ctk.CTkEntry(frame, width=300)
        entry.insert(0, str(valor))
        entry.pack(side="left", padx=5)

        self.entries[key] = entry

    def _guardar(self):
        data = {}
        for key, entry in self.entries.items():
            valor = entry.get().strip()
            if key in ("dias_por_vencer", "frecuencia_backup"):
                try:
                    data[key] = int(valor)
                except ValueError:
                    messagebox.showerror("Error", f"{key} debe ser un número entero")
                    return
            elif key == "porcentaje_mora":
                try:
                    data[key] = float(valor)
                except ValueError:
                    messagebox.showerror("Error", "El porcentaje de mora debe ser un número")
                    return
            else:
                data[key] = valor

        data["mora_habilitada"] = 1 if self.mora_switch.get() else 0
        data["permitir_multiples_becas"] = 1 if self.becas_switch.get() else 0
        data["backup_automatico"] = 1 if self.backup_switch.get() else 0

        exito, msg = configuracion_controller.actualizar_configuracion(data)
        if exito:
            messagebox.showinfo("Éxito", msg)
        else:
            messagebox.showerror("Error", msg)
