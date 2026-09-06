import customtkinter as ctk
from controllers import pago_controller, login_controller
from controllers import estudiante_controller, matricula_controller
from widgets.date_picker import DatePicker


class PagoView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._matriculas_map = {}
        self._cuotas_map = {}
        self._crear_widgets()
        self._cargar_pagos()

    def _crear_widgets(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_lista = self.tabview.add("Pagos")
        self.tab_form = self.tabview.add("Registrar Pago")
        self.tab_morosos = self.tabview.add("Morosos")

        self._crear_tab_lista()
        self._crear_tab_formulario()
        self._crear_tab_morosos()

    def _crear_tab_lista(self):
        header = ctk.CTkFrame(self.tab_lista, fg_color="white", corner_radius=10, border_width=1, border_color="#E5E7EB")
        header.pack(fill="x", padx=8, pady=8)

        ctk.CTkLabel(header, text="💰 Historial de Pagos", font=ctk.CTkFont(size=22, weight="bold"), text_color="#1F0A33").pack(side="left", padx=12, pady=10)
        ctk.CTkLabel(header, text="Pagos registrados y filtros por fecha", font=ctk.CTkFont(size=12), text_color="#6B5B7B").pack(side="left", padx=10)
        from utils.ui_helpers import crear_boton_interactivo
        crear_boton_interactivo(header, text="+ Nuevo Pago", width=130, height=36, command=self._nuevo_pago, fg_color="#7C3AED").pack(side="right", padx=8, pady=8)

        filtros = ctk.CTkFrame(self.tab_lista, fg_color="white", corner_radius=10, border_width=1, border_color="#E5E7EB")
        filtros.pack(fill="x", padx=8, pady=6)

        self.date_picker_inicio = DatePicker(filtros, label_text="Fecha Inicio:", default="start_of_month")
        self.date_picker_inicio.pack(side="left", padx=(12, 10))

        self.date_picker_fin = DatePicker(filtros, label_text="Fecha Fin:", default="today")
        self.date_picker_fin.pack(side="left", padx=(0, 10))

        from utils.ui_helpers import crear_boton_interactivo
        crear_boton_interactivo(filtros, text="🔍 Buscar", width=90, command=self._buscar_por_fecha, fg_color="#7C3AED").pack(side="left", padx=5)
        crear_boton_interactivo(filtros, text="🧹 Limpiar", width=90, fg_color="#E5E7EB", hover_color="#DDD6E5", text_color="#1F0A33", command=self._limpiar_fechas).pack(side="left", padx=5)
        ctk.CTkLabel(filtros, text="|", text_color="#E5E7EB").pack(side="left", padx=8)
        self.entry_busqueda = ctk.CTkEntry(filtros, placeholder_text="🔍 Buscar por DNI, recibo o método...", width=260, border_color="#DDD6E5")
        self.entry_busqueda.pack(side="left", padx=5)
        self.entry_busqueda.bind("<KeyRelease>", self._on_busqueda_cambiar)

        self.scroll_pagos = ctk.CTkScrollableFrame(self.tab_lista, fg_color="#F8F5FA")
        self.scroll_pagos.pack(fill="both", expand=True, padx=8, pady=6)

        self.label_status = ctk.CTkLabel(self.tab_lista, text="⏳ Cargando pagos...", font=ctk.CTkFont(size=13, weight="bold"), text_color="#6B5B7B")
        self.label_status.pack(pady=4)

    def _crear_tab_formulario(self):
        scroll = ctk.CTkScrollableFrame(self.tab_form)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="Registrar Pago",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(scroll, text="Estudiante *", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.combo_estudiante = ctk.CTkComboBox(
            scroll, width=400, values=["Cargando..."],
            command=self._on_estudiante_cambiado,
        )
        self.combo_estudiante.pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(scroll, text="Cuota pendiente *", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.combo_cuota = ctk.CTkComboBox(scroll, width=400, values=["Seleccionar estudiante primero"])
        self.combo_cuota.pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(scroll, text="Monto a pagar (S/) *", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.entry_monto = ctk.CTkEntry(scroll, placeholder_text="0.00", width=200)
        self.entry_monto.pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(scroll, text="Método de pago *", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.combo_metodo = ctk.CTkComboBox(
            scroll, width=200,
            values=["EFECTIVO", "YAPE", "PLIN", "TRANSFERENCIA"],
        )
        self.combo_metodo.set("EFECTIVO")
        self.combo_metodo.pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(scroll, text="Observación (opcional)", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.entry_observacion = ctk.CTkEntry(scroll, placeholder_text="Referencia o nota", width=400)
        self.entry_observacion.pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(scroll, text="Comprobante foto (obligatorio si YAPE/PLIN/TRANSFERENCIA)", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.btn_comprobante = ctk.CTkButton(scroll, text="Seleccionar comprobante", width=200, command=self._elegir_comprobante)
        self.btn_comprobante.pack(anchor="w", pady=3)
        self.label_comprobante = ctk.CTkLabel(scroll, text="Sin comprobante", text_color="gray")
        self.label_comprobante.pack(anchor="w")
        self._comprobante_path = None

        self.label_form_status = ctk.CTkLabel(scroll, text="", font=ctk.CTkFont(size=12))
        self.label_form_status.pack(anchor="w", pady=5)

        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(anchor="w", pady=10)

        ctk.CTkButton(
            btn_frame, text="Registrar Pago", width=130,
            command=self._registrar_pago,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, text="Cancelar", width=100, fg_color="gray",
            command=lambda: self.tabview.set("Pagos"),
        ).pack(side="left", padx=5)

    def _crear_tab_morosos(self):
        header = ctk.CTkFrame(self.tab_morosos, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            header, text="Cuotas Vencidas",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            header, text="Actualizar", width=100,
            command=self._cargar_morosos,
        ).pack(side="right")

        self.scroll_morosos = ctk.CTkScrollableFrame(self.tab_morosos)
        self.scroll_morosos.pack(fill="both", expand=True, padx=5, pady=5)

        self.label_status_morosos = ctk.CTkLabel(self.tab_morosos, text="", font=ctk.CTkFont(size=11))
        self.label_status_morosos.pack(pady=3)

    def _cargar_pagos(self, pagos=None):
        self._pagos_actuales = pagos if pagos is not None else pago_controller.listar_pagos()
        self._renderizar_pagos(self._pagos_actuales)

    def _on_busqueda_cambiar(self, event=None):
        texto = self.entry_busqueda.get().strip().lower()
        pagos = self._pagos_actuales if hasattr(self, '_pagos_actuales') else pago_controller.listar_pagos()

        if texto:
            filtrados = []
            for p in pagos:
                recibo = str(p.get('numero_recibo', '')).lower()
                metodo = str(p.get('metodo_pago', '')).lower()
                if texto in recibo or texto in metodo:
                    filtrados.append(p)
            self._renderizar_pagos(filtrados)
        else:
            self._renderizar_pagos(pagos)

    def _renderizar_pagos(self, pagos):
        for widget in self.scroll_pagos.winfo_children():
            widget.destroy()

        if not pagos:
            ctk.CTkLabel(self.scroll_pagos, text="📭 No se encontraron pagos", font=ctk.CTkFont(size=14), text_color="gray").pack(pady=30)
            ctk.CTkLabel(self.scroll_pagos, text="Registra tu primer pago con + Nuevo Pago", font=ctk.CTkFont(size=12), text_color="#9CA3AF").pack()
            self.label_status.configure(text="Total: 0 pagos • Prueba filtros de fecha")
            return
        for pago in pagos:
            self._crear_card_pago(pago)
        self.label_status.configure(text=f"✅ Total: {len(pagos)} pago(s) • {sum(p.get('monto_total',0) for p in pagos):.2f} S/ en total")

    def _crear_card_pago(self, pago):
        from utils.ui_helpers import crear_card_interactiva
        card = crear_card_interactiva(self.scroll_pagos)
        card.pack(fill="x", padx=6, pady=4)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=12, pady=10)

        ctk.CTkLabel(info, text=f"🧾 Recibo: {pago.get('numero_recibo', '')}", font=ctk.CTkFont(size=15, weight="bold"), text_color="#1F0A33").pack(anchor="w")
        ctk.CTkLabel(info, text=f"💵 S/{pago.get('monto_total', 0):.2f}  •  {pago.get('metodo_pago', '')}  •  📅 {pago.get('fecha_pago', '')}", font=ctk.CTkFont(size=13), text_color="#374151").pack(anchor="w", pady=2)
        ctk.CTkLabel(info, text=f"👤 Registrado por: {pago.get('username', '')}", font=ctk.CTkFont(size=12), text_color="#6B5B7B").pack(anchor="w")
        # badge monto
        badge = ctk.CTkFrame(card, fg_color="#F3E8FF", corner_radius=8)
        badge.pack(side="right", padx=10)
        ctk.CTkLabel(badge, text=f"S/{pago.get('monto_total',0):.2f}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#7C3AED").pack(padx=10, pady=6)

    def _buscar_por_fecha(self):
        fecha_inicio = self.date_picker_inicio.get()
        fecha_fin = self.date_picker_fin.get()

        if not fecha_inicio or not fecha_fin:
            self.label_status.configure(text="Selecciona ambas fechas", text_color="orange")
            return

        if fecha_inicio > fecha_fin:
            self.label_status.configure(text="La fecha de inicio debe ser anterior a la fecha fin", text_color="red")
            return

        pagos = pago_controller.listar_por_fecha(fecha_inicio, fecha_fin)
        self._cargar_pagos(pagos)

    def _limpiar_fechas(self):
        self.date_picker_inicio.delete()
        self.date_picker_fin.delete()
        self.label_status.configure(text="")

    def _nuevo_pago(self):
        self._cargar_combo_estudiantes()
        self.entry_monto.delete(0, "end")
        self.label_form_status.configure(text="")
        self.tabview.set("Registrar Pago")

    def _cargar_combo_estudiantes(self):
        from controllers import pago_controller
        matriculas = pago_controller.listar_matriculas_activas()
        nombres = [f"{m.get('nombres', '')} {m.get('apellidos', '')} - {m.get('tarifa_nombre', '')}" for m in matriculas]
        self.combo_estudiante.configure(values=nombres if nombres else ["Sin matrículas activas"])
        self._matriculas_map = {n: m["id_matricula"] for n, m in zip(nombres, matriculas)}

    def _on_estudiante_cambiado(self, selection):
        self._cargar_combo_cuotas(selection)

    def _cargar_combo_cuotas(self, selection):
        id_mat = self._matriculas_map.get(selection)
        if not id_mat:
            return

        cuotas = pago_controller.obtener_cuotas_pendientes(id_mat)

        nombres = []
        self._cuotas_map = {}
        for c in cuotas:
            nombre = f"{c['periodo']} - S/{c['saldo']:.2f} ({c['estado']})"
            nombres.append(nombre)
            self._cuotas_map[nombre] = c["id_cuota"]

        self.combo_cuota.configure(values=nombres if nombres else ["Sin cuotas pendientes"])

    def _registrar_pago(self):
        est_selection = self.combo_estudiante.get()
        id_mat = self._matriculas_map.get(est_selection)
        if not id_mat:
            self.label_form_status.configure(text="Seleccione un estudiante", text_color="red")
            return

        cuota_selection = self.combo_cuota.get()
        id_cuota = self._cuotas_map.get(cuota_selection)
        if not id_cuota:
            self.label_form_status.configure(text="Seleccione una cuota", text_color="red")
            return

        monto_str = self.entry_monto.get().strip()
        if not monto_str:
            self.label_form_status.configure(text="Ingrese el monto", text_color="red")
            return

        usuario = login_controller.obtener_usuario_actual()
        if not usuario:
            self.label_form_status.configure(text="Sesión no válida", text_color="red")
            return

        comprobante = self._comprobante_path
        if self.combo_metodo.get() != "EFECTIVO" and not comprobante:
            self.label_form_status.configure(text="Suba comprobante para YAPE/PLIN/TRANSFERENCIA (RN-042)", text_color="orange")
            return
        data = {
            "id_usuario": usuario["id_usuario"],
            "id_cuota": id_cuota,
            "monto_pagado": monto_str,
            "metodo_pago": self.combo_metodo.get(),
            "observacion": self.entry_observacion.get().strip(),
            "comprobante_path": comprobante,
        }

        exito, msg, id_pago = pago_controller.registrar_pago(data)

        if exito:
            self.label_form_status.configure(text=msg, text_color="green")
            self._cargar_pagos()
            self.entry_monto.delete(0, "end")
            self.entry_observacion.delete(0, "end")
            self._comprobante_path = None
            self.label_comprobante.configure(text="Sin comprobante")
        else:
            self.label_form_status.configure(text=msg, text_color="red")

    def _elegir_comprobante(self):
        from tkinter import filedialog
        import os
        from utils.constants import COMPROBANTES_DIR
        path = filedialog.askopenfilename(filetypes=[("Imagen","*.jpg *.jpeg *.png"),("Todos","*.*")])
        if path:
            os.makedirs(COMPROBANTES_DIR, exist_ok=True)
            self._comprobante_path = path
            self.label_comprobante.configure(text=os.path.basename(path))

    def _cargar_morosos(self):
        for widget in self.scroll_morosos.winfo_children():
            widget.destroy()

        morosos = pago_controller.obtener_cuotas_vencidas()

        if not morosos:
            ctk.CTkLabel(
                self.scroll_morosos, text="No hay cuotas vencidas",
                text_color="green",
            ).pack(pady=20)
            self.label_status_morosos.configure(text="Total: 0")
            return

        for m in morosos:
            card = ctk.CTkFrame(self.scroll_morosos)
            card.pack(fill="x", padx=5, pady=3)

            ctk.CTkLabel(
                card,
                text=f"{m.get('nombres', '')} {m.get('apellidos', '')} - DNI: {m.get('dni', '')}",
                font=ctk.CTkFont(size=13, weight="bold"),
            ).pack(anchor="w", padx=10, pady=(5, 0))

            ctk.CTkLabel(
                card,
                text=f"Cuota: {m.get('periodo', '')} | Venció: {m.get('fecha_vencimiento', '')} | "
                     f"Saldo: S/{m.get('saldo', 0):.2f}",
                font=ctk.CTkFont(size=12), text_color="red",
            ).pack(anchor="w", padx=10, pady=(0, 5))

        self.label_status_morosos.configure(text=f"Total: {len(morosos)} cuota(s) vencida(s)")
