import customtkinter as ctk
from controllers import tarifa_controller, configuracion_controller


class TarifaView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._cats_map = {}
        self._crear_widgets()
        self._cargar_tarifas()

    def _crear_widgets(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            header, text="Tarifas",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            header, text="+ Nueva", width=100,
            command=self._nueva_tarifa,
        ).pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=5, pady=5)

        self.label_status = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11))
        self.label_status.pack(pady=3)

        self._crear_formulario()

    def _crear_formulario(self):
        self.form_window = ctk.CTkToplevel(self)
        self.form_window.title("Nueva Tarifa")
        self.form_window.geometry("420x500")
        self.form_window.withdraw()

        scroll = ctk.CTkScrollableFrame(self.form_window)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="Nueva Tarifa",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(scroll, text="Categoría:").pack(anchor="w")
        self.combo_categoria = ctk.CTkComboBox(scroll, width=380, values=["Cargando..."])
        self.combo_categoria.pack(anchor="w", pady=3)

        ctk.CTkLabel(scroll, text="Nombre:").pack(anchor="w")
        self.entry_nombre = ctk.CTkEntry(scroll, placeholder_text="Nombre de la tarifa", width=380)
        self.entry_nombre.pack(anchor="w", pady=3)

        ctk.CTkLabel(scroll, text="Monto (S/):").pack(anchor="w")
        self.entry_monto = ctk.CTkEntry(scroll, placeholder_text="0.00", width=380)
        self.entry_monto.pack(anchor="w", pady=3)

        ctk.CTkLabel(scroll, text="Descripción:").pack(anchor="w")
        self.entry_descripcion = ctk.CTkEntry(scroll, placeholder_text="Opcional", width=380)
        self.entry_descripcion.pack(anchor="w", pady=3)

        ctk.CTkLabel(scroll, text="Observaciones:").pack(anchor="w")
        self.entry_observaciones = ctk.CTkEntry(scroll, placeholder_text="Opcional", width=380)
        self.entry_observaciones.pack(anchor="w", pady=3)

        self.label_form_status = ctk.CTkLabel(scroll, text="", font=ctk.CTkFont(size=12))
        self.label_form_status.pack(anchor="w", pady=5)

        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(anchor="w", pady=10)

        ctk.CTkButton(
            btn_frame, text="Guardar", width=120,
            command=self._guardar_tarifa,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, text="Cancelar", width=100, fg_color="gray",
            command=lambda: self.form_window.withdraw(),
        ).pack(side="left", padx=5)

    def _cargar_categorias(self):
        cats = configuracion_controller.listar_categorias()
        nombres = [f"{c['nombre']} ({c['edad_min']}-{c['edad_max']} años)" for c in cats]
        self.combo_categoria.configure(values=nombres if nombres else ["Sin categorías"])
        self._cats_map = {n: c["id_categoria"] for n, c in zip(nombres, cats)}

    def _nueva_tarifa(self):
        self._cargar_categorias()
        self.entry_nombre.delete(0, "end")
        self.entry_monto.delete(0, "end")
        self.entry_descripcion.delete(0, "end")
        self.entry_observaciones.delete(0, "end")
        self.label_form_status.configure(text="")
        self.form_window.deiconify()

    def _guardar_tarifa(self):
        cat_selection = self.combo_categoria.get()
        id_categoria = self._cats_map.get(cat_selection)
        if not id_categoria:
            self.label_form_status.configure(text="Seleccione una categoría", text_color="red")
            return

        nombre = self.entry_nombre.get().strip()
        if not nombre:
            self.label_form_status.configure(text="El nombre es obligatorio", text_color="red")
            return

        try:
            monto = float(self.entry_monto.get().strip() or "0")
            if monto <= 0:
                self.label_form_status.configure(text="El monto debe ser mayor a 0", text_color="red")
                return
        except ValueError:
            self.label_form_status.configure(text="Monto no válido", text_color="red")
            return

        data = {
            "id_categoria": id_categoria,
            "nombre": nombre,
            "monto": monto,
            "descripcion": self.entry_descripcion.get().strip(),
            "observaciones": self.entry_observaciones.get().strip(),
        }

        exito, msg, _ = tarifa_controller.crear_tarifa(data)
        if exito:
            self.label_form_status.configure(text=msg, text_color="green")
            self.form_window.withdraw()
            self._cargar_tarifas()
        else:
            self.label_form_status.configure(text=msg, text_color="red")

    def _cargar_tarifas(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        tarifas = tarifa_controller.listar_tarifas_activas()

        if not tarifas:
            ctk.CTkLabel(
                self.scroll, text="No hay tarifas registradas",
                text_color="gray",
            ).pack(pady=20)
            self.label_status.configure(text="Total: 0")
            return

        for t in tarifas:
            self._crear_card(t)

        self.label_status.configure(text=f"Total: {len(tarifas)} tarifa(s)")

    def _crear_card(self, t):
        card = ctk.CTkFrame(self.scroll)
        card.pack(fill="x", padx=5, pady=3)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=10, pady=8)

        ctk.CTkLabel(
            info,
            text=f"{t.get('categoria_nombre', '')} - {t['nombre']}",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w")

        desc = t.get("descripcion", "") or ""
        monto_line = f"Monto: S/{t['monto']:.2f}"
        if desc:
            monto_line += f" | {desc}"
        ctk.CTkLabel(
            info, text=monto_line,
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(anchor="w")

        if t.get("observaciones"):
            ctk.CTkLabel(
                info, text=f"Obs: {t['observaciones']}",
                font=ctk.CTkFont(size=11), text_color="gray",
            ).pack(anchor="w")

        botones = ctk.CTkFrame(card, fg_color="transparent")
        botones.pack(side="right", padx=5, pady=5)

        ctk.CTkButton(
            botones, text="Editar", width=80, height=28,
            command=lambda t=t: self._editar_tarifa(t),
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            botones, text="Desactivar", width=90, height=28,
            fg_color="#d9534f",
            command=lambda t=t: self._desactivar_tarifa(t),
        ).pack(side="left", padx=2)

    def _editar_tarifa(self, t):
        pass

    def _desactivar_tarifa(self, t):
        exito, msg = tarifa_controller.desactivar_tarifa(t["id_tarifa"])
        if exito:
            self._cargar_tarifas()
