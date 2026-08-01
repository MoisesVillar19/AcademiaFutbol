import customtkinter as ctk
from controllers import pago_controller, login_controller
from controllers import estudiante_controller, matricula_controller


class PagoView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
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
        header = ctk.CTkFrame(self.tab_lista, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            header, text="Historial de Pagos",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            header, text="+ Nuevo Pago", width=120,
            command=self._nuevo_pago,
        ).pack(side="right")

        filtros = ctk.CTkFrame(self.tab_lista, fg_color="transparent")
        filtros.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(filtros, text="Desde:").pack(side="left")
        self.entry_fecha_inicio = ctk.CTkEntry(filtros, placeholder_text="YYYY-MM-DD", width=120)
        self.entry_fecha_inicio.pack(side="left", padx=5)

        ctk.CTkLabel(filtros, text="Hasta:").pack(side="left")
        self.entry_fecha_fin = ctk.CTkEntry(filtros, placeholder_text="YYYY-MM-DD", width=120)
        self.entry_fecha_fin.pack(side="left", padx=5)

        ctk.CTkButton(
            filtros, text="Buscar", width=80,
            command=self._buscar_por_fecha,
        ).pack(side="left", padx=5)

        self.scroll_pagos = ctk.CTkScrollableFrame(self.tab_lista)
        self.scroll_pagos.pack(fill="both", expand=True, padx=5, pady=5)

        self.label_status = ctk.CTkLabel(self.tab_lista, text="", font=ctk.CTkFont(size=11))
        self.label_status.pack(pady=3)

    def _crear_tab_formulario(self):
        scroll = ctk.CTkScrollableFrame(self.tab_form)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="Registrar Pago",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(scroll, text="Estudiante:").pack(anchor="w")
        self.combo_estudiante = ctk.CTkComboBox(scroll, width=400, values=["Cargando..."])
        self.combo_estudiante.pack(anchor="w", pady=3)

        ctk.CTkLabel(scroll, text="Cuota pendiente:").pack(anchor="w")
        self.combo_cuota = ctk.CTkComboBox(scroll, width=400, values=["Seleccionar estudiante primero"])
        self.combo_cuota.pack(anchor="w", pady=3)

        ctk.CTkLabel(scroll, text="Monto a pagar (S/):").pack(anchor="w")
        self.entry_monto = ctk.CTkEntry(scroll, placeholder_text="0.00", width=200)
        self.entry_monto.pack(anchor="w", pady=3)

        ctk.CTkLabel(scroll, text="Método de pago:").pack(anchor="w")
        self.combo_metodo = ctk.CTkComboBox(
            scroll, width=200,
            values=["EFECTIVO", "YAPE", "PLIN", "TRANSFERENCIA"],
        )
        self.combo_metodo.set("EFECTIVO")
        self.combo_metodo.pack(anchor="w", pady=3)

        ctk.CTkLabel(scroll, text="Observación (opcional):").pack(anchor="w")
        self.entry_observacion = ctk.CTkEntry(scroll, placeholder_text="Observación", width=400)
        self.entry_observacion.pack(anchor="w", pady=3)

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
        for widget in self.scroll_pagos.winfo_children():
            widget.destroy()

        if pagos is None:
            pagos = pago_controller.listar_pagos()

        if not pagos:
            ctk.CTkLabel(
                self.scroll_pagos, text="No hay pagos registrados",
                text_color="gray",
            ).pack(pady=20)
            self.label_status.configure(text="Total: 0")
            return

        for pago in pagos:
            self._crear_card_pago(pago)

        self.label_status.configure(text=f"Total: {len(pagos)} pago(s)")

    def _crear_card_pago(self, pago):
        card = ctk.CTkFrame(self.scroll_pagos)
        card.pack(fill="x", padx=5, pady=3)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=10, pady=8)

        ctk.CTkLabel(
            info,
            text=f"Recibo: {pago.get('numero_recibo', '')}",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            info,
            text=f"S/{pago.get('monto_total', 0):.2f} | {pago.get('metodo_pago', '')} | "
                 f"{pago.get('fecha_pago', '')}",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(anchor="w")

        ctk.CTkLabel(
            info,
            text=f"Registrado por: {pago.get('username', '')}",
            font=ctk.CTkFont(size=11), text_color="gray",
        ).pack(anchor="w")

    def _buscar_por_fecha(self):
        fecha_inicio = self.entry_fecha_inicio.get().strip()
        fecha_fin = self.entry_fecha_fin.get().strip()

        if not fecha_inicio or not fecha_fin:
            return

        pagos = pago_controller.listar_por_fecha(fecha_inicio, fecha_fin)
        self._cargar_pagos(pagos)

    def _nuevo_pago(self):
        self._cargar_combo_estudiantes()
        self.entry_monto.delete(0, "end")
        self.label_form_status.configure(text="")
        self.tabview.set("Registrar Pago")

    def _cargar_combo_estudiantes(self):
        from repositories import matricula_repository
        matriculas = matricula_repository.obtener_activas()
        nombres = [f"{m.get('nombres', '')} {m.get('apellidos', '')} - {m.get('tarifa_nombre', '')} (Mat:{m['id_matricula']})" for m in matriculas]
        self.combo_estudiante.configure(values=nombres if nombres else ["Sin matrículas activas"])
        self._matriculas_map = {n: m["id_matricula"] for n, m in zip(nombres, matriculas)}

    def _cargar_combo_cuotas(self, selection):
        id_mat = self._matriculas_map.get(selection)
        if not id_mat:
            return

        from services import cuota_service
        cuotas = cuota_service.obtener_cuotas_pendientes(id_mat)

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

        data = {
            "id_usuario": usuario["id_usuario"],
            "id_cuota": id_cuota,
            "monto_pagado": monto_str,
            "metodo_pago": self.combo_metodo.get(),
            "observacion": self.entry_observacion.get().strip(),
        }

        exito, msg, id_pago = pago_controller.registrar_pago(data)

        if exito:
            self.label_form_status.configure(text=msg, text_color="green")
            self._cargar_pagos()
            self.entry_monto.delete(0, "end")
            self.entry_observacion.delete(0, "end")
        else:
            self.label_form_status.configure(text=msg, text_color="red")

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
