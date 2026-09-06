import customtkinter as ctk
from tkinter import messagebox
from controllers import configuracion_controller, categoria_controller
from utils.dates import calculate_age


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

        precios_frame = ctk.CTkFrame(self.contenido)
        precios_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            precios_frame, text="Precios Flexibles (S/) — editable sin código",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self._crear_campo(precios_frame, "precio_inscripcion", "Inscripción (nuevo, incluye camiseta)",
                          str(config.get("precio_inscripcion", 100)))
        self._crear_campo(precios_frame, "precio_mensualidad", "Mensualidad (antiguo, mensual)",
                          str(config.get("precio_mensualidad", 100)))
        self._crear_campo(precios_frame, "precio_reingreso", "Reingreso (con uniforme anterior)",
                          str(config.get("precio_reingreso", 100)))
        self._crear_campo(precios_frame, "precio_uniforme", "Uniforme base",
                          str(config.get("precio_uniforme", 20)))
        self._crear_campo(precios_frame, "tasa_campeonato", "Tasa campeonato",
                          str(config.get("tasa_campeonato", 15)))
        self._crear_campo(precios_frame, "arbitraje_por_equipo", "Arbitraje por equipo",
                          str(config.get("arbitraje_por_equipo", 15)))
        self._crear_campo(precios_frame, "pago_profesor", "Pago profesor",
                          str(config.get("pago_profesor", 200)))

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

        categorias_frame = ctk.CTkFrame(self.contenido)
        categorias_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            categorias_frame, text="Categorías de Edad",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self._cargar_categorias(categorias_frame)

        ctk.CTkButton(
            categorias_frame, text="+ Nueva Categoría", width=150,
            command=self._nueva_categoria,
        ).pack(anchor="w", padx=10, pady=5)

        uniformes_frame = ctk.CTkFrame(self.contenido)
        uniformes_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            uniformes_frame, text="Tipos de Uniforme (flexible)",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self._cargar_tipos_uniforme(uniformes_frame)

        ctk.CTkButton(
            uniformes_frame, text="+ Nuevo Tipo Uniforme", width=180,
            command=self._nuevo_tipo_uniforme,
        ).pack(anchor="w", padx=10, pady=5)

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
            elif key in ("porcentaje_mora", "precio_inscripcion", "precio_mensualidad", "precio_reingreso", "precio_uniforme", "tasa_campeonato", "arbitraje_por_equipo", "pago_profesor"):
                try:
                    data[key] = float(valor)
                except ValueError:
                    messagebox.showerror("Error", f"{key} debe ser un número")
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

    def _cargar_categorias(self, parent):
        cats = categoria_controller.listar_categorias()
        if not cats:
            ctk.CTkLabel(parent, text="No hay categorías", text_color="gray").pack(
                anchor="w", padx=10, pady=3
            )
            return
        for cat in cats:
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(
                row,
                text=f"{cat['nombre']}  |  Edad: {cat['edad_min']}-{cat['edad_max']} años",
                font=ctk.CTkFont(size=12),
            ).pack(side="left")

            ctk.CTkButton(
                row, text="Editar", width=70, height=28,
                command=lambda c=cat: self._editar_categoria(c),
            ).pack(side="right", padx=2)

            ctk.CTkButton(
                row, text="Desactivar", width=90, height=28,
                fg_color="#d9534f",
                command=lambda c=cat: self._desactivar_categoria(c),
            ).pack(side="right", padx=2)

    def _nueva_categoria(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nueva Categoría")
        dialog.geometry("350x250")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Nombre:").pack(anchor="w", padx=15, pady=(15, 2))
        entry_nombre = ctk.CTkEntry(dialog, width=300)
        entry_nombre.pack(padx=15)

        ctk.CTkLabel(dialog, text="Edad mínima:").pack(anchor="w", padx=15, pady=(10, 2))
        entry_min = ctk.CTkEntry(dialog, width=300)
        entry_min.pack(padx=15)

        ctk.CTkLabel(dialog, text="Edad máxima:").pack(anchor="w", padx=15, pady=(10, 2))
        entry_max = ctk.CTkEntry(dialog, width=300)
        entry_max.pack(padx=15)

        label_status = ctk.CTkLabel(dialog, text="", font=ctk.CTkFont(size=12))
        label_status.pack(padx=15, pady=5)

        def guardar():
            nombre = entry_nombre.get().strip()
            edad_min = entry_min.get().strip()
            edad_max = entry_max.get().strip()

            exito, msg, _ = categoria_controller.crear_categoria({
                "nombre": nombre,
                "edad_min": edad_min,
                "edad_max": edad_max,
            })
            if exito:
                dialog.destroy()
                self._cargar_configuracion()
            else:
                label_status.configure(text=msg, text_color="red")

        ctk.CTkButton(dialog, text="Guardar", width=120, command=guardar).pack(pady=10)

    def _editar_categoria(self, cat):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Editar Categoría")
        dialog.geometry("350x250")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Nombre:").pack(anchor="w", padx=15, pady=(15, 2))
        entry_nombre = ctk.CTkEntry(dialog, width=300)
        entry_nombre.insert(0, cat["nombre"])
        entry_nombre.pack(padx=15)

        ctk.CTkLabel(dialog, text="Edad mínima:").pack(anchor="w", padx=15, pady=(10, 2))
        entry_min = ctk.CTkEntry(dialog, width=300)
        entry_min.insert(0, str(cat["edad_min"]))
        entry_min.pack(padx=15)

        ctk.CTkLabel(dialog, text="Edad máxima:").pack(anchor="w", padx=15, pady=(10, 2))
        entry_max = ctk.CTkEntry(dialog, width=300)
        entry_max.insert(0, str(cat["edad_max"]))
        entry_max.pack(padx=15)

        label_status = ctk.CTkLabel(dialog, text="", font=ctk.CTkFont(size=12))
        label_status.pack(padx=15, pady=5)

        def guardar():
            exito, msg = categoria_controller.editar_categoria(cat["id_categoria"], {
                "nombre": entry_nombre.get().strip(),
                "edad_min": entry_min.get().strip(),
                "edad_max": entry_max.get().strip(),
            })
            if exito:
                dialog.destroy()
                self._cargar_configuracion()
            else:
                label_status.configure(text=msg, text_color="red")

        ctk.CTkButton(dialog, text="Guardar", width=120, command=guardar).pack(pady=10)

    def _desactivar_categoria(self, cat):
        confirm = messagebox.askyesno(
            "Confirmar",
            f"¿Desactivar la categoría '{cat['nombre']}'?"
        )
        if confirm:
            exito, msg = categoria_controller.desactivar_categoria(cat["id_categoria"])
            if exito:
                self._cargar_configuracion()
            else:
                messagebox.showerror("Error", msg)

    def _cargar_tipos_uniforme(self, parent):
        try:
            from controllers import tipo_uniforme_controller
            tipos = tipo_uniforme_controller.listar_tipos()
        except Exception:
            from services import tipo_uniforme_service
            tipos = tipo_uniforme_service.listar_tipos()
        for t in tipos:
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row, text=f"{t['nombre']} - {t.get('descripcion','')}", font=ctk.CTkFont(size=12)).pack(side="left")
            ctk.CTkButton(row, text="Desactivar", width=90, height=28, fg_color="#d9534f",
                          command=lambda x=t: self._desactivar_tipo_uniforme(x)).pack(side="right", padx=2)

    def _nuevo_tipo_uniforme(self):
        dialog = ctk.CTkInputDialog(text="Nombre del tipo de uniforme:", title="Nuevo Tipo Uniforme")
        nombre = dialog.get_input()
        if not nombre:
            return
        try:
            from controllers import tipo_uniforme_controller
            exito, msg, _ = tipo_uniforme_controller.crear_tipo({"nombre": nombre})
        except Exception:
            from services import tipo_uniforme_service
            exito, msg, _ = tipo_uniforme_service.crear_tipo_uniforme({"nombre": nombre})
        if exito:
            self._cargar_configuracion()
        else:
            messagebox.showerror("Error", msg)

    def _desactivar_tipo_uniforme(self, t):
        if messagebox.askyesno("Confirmar", f"¿Desactivar '{t['nombre']}'?"):
            try:
                from controllers import tipo_uniforme_controller
                exito, msg = tipo_uniforme_controller.desactivar_tipo(t["id_tipo_uniforme"])
            except Exception:
                from services import tipo_uniforme_service
                exito, msg = tipo_uniforme_service.desactivar_tipo(t["id_tipo_uniforme"])
            if exito:
                self._cargar_configuracion()
            else:
                messagebox.showerror("Error", msg)
