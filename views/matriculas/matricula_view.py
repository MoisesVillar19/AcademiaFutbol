import customtkinter as ctk
from controllers import matricula_controller, estudiante_controller


class MatriculaView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._estudiantes_map = {}
        self._tarifas_map = {}
        self._becas_map = {}
        self._matriculas_map = {}
        self._crear_widgets()
        self._cargar_matriculas()

    def _crear_widgets(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_lista = self.tabview.add("Matrículas")
        self.tab_form = self.tabview.add("Registrar")
        self.tab_cuotas = self.tabview.add("Cuotas")

        self._crear_tab_lista()
        self._crear_tab_formulario()
        self._crear_tab_cuotas()

    def _crear_tab_lista(self):
        header = ctk.CTkFrame(self.tab_lista, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            header, text="Matrículas Activas",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            header, text="+ Nueva", width=100,
            command=self._nueva_matricula,
        ).pack(side="right")

        filtros = ctk.CTkFrame(self.tab_lista, fg_color="transparent")
        filtros.pack(fill="x", padx=5, pady=5)

        self.entry_busqueda = ctk.CTkEntry(
            filtros, placeholder_text="Buscar por DNI, Carnet o nombre...",
            width=250,
        )
        self.entry_busqueda.pack(side="left", padx=5)
        self.entry_busqueda.bind("<KeyRelease>", self._on_busqueda_cambiar)

        self.scroll_matriculas = ctk.CTkScrollableFrame(self.tab_lista)
        self.scroll_matriculas.pack(fill="both", expand=True, padx=5, pady=5)

        self.label_status = ctk.CTkLabel(self.tab_lista, text="", font=ctk.CTkFont(size=11))
        self.label_status.pack(pady=3)

    def _crear_tab_formulario(self):
        scroll = ctk.CTkScrollableFrame(self.tab_form)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="Nueva Matrícula",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(scroll, text="Estudiante *", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.combo_estudiante = ctk.CTkComboBox(
            scroll, width=400, values=["Cargando..."],
            command=self._on_estudiante_changed,
        )
        self.combo_estudiante.pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(scroll, text="Tarifa *", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.combo_tarifa = ctk.CTkComboBox(scroll, width=400, values=["Cargando..."])
        self.combo_tarifa.pack(anchor="w", pady=(0, 5))

        row1 = ctk.CTkFrame(scroll, fg_color="transparent")
        row1.pack(fill="x", anchor="w", pady=3)

        ctk.CTkLabel(row1, text="Monto pactado (S/):").pack(side="left")
        self.entry_monto_pactado = ctk.CTkEntry(row1, placeholder_text="Opcional", width=120)
        self.entry_monto_pactado.pack(side="left", padx=10)

        ctk.CTkLabel(row1, text="Día vencimiento:").pack(side="left", padx=(20, 0))
        self.entry_dia_venc = ctk.CTkEntry(row1, placeholder_text="1-31", width=60)
        self.entry_dia_venc.insert(0, "1")
        self.entry_dia_venc.pack(side="left", padx=5)

        ctk.CTkLabel(scroll, text="Beca (opcional):").pack(anchor="w")
        self.combo_beca = ctk.CTkComboBox(scroll, width=400, values=["Ninguna"])
        self.combo_beca.pack(anchor="w", pady=3)

        self.label_form_status = ctk.CTkLabel(scroll, text="", font=ctk.CTkFont(size=12))
        self.label_form_status.pack(anchor="w", pady=5)

        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(anchor="w", pady=10)

        ctk.CTkButton(
            btn_frame, text="Registrar Matrícula", width=150,
            command=self._registrar_matricula,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, text="Cancelar", width=100, fg_color="gray",
            command=lambda: self.tabview.set("Matrículas"),
        ).pack(side="left", padx=5)

    def _crear_tab_cuotas(self):
        header = ctk.CTkFrame(self.tab_cuotas, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            header, text="Cuotas por Matrícula",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(side="left")

        self.combo_matricula_cuotas = ctk.CTkComboBox(
            self.tab_cuotas, width=400,
            values=["Seleccionar matrícula..."],
            command=self._cargar_cuotas,
        )
        self.combo_matricula_cuotas.set("Seleccionar matrícula...")
        self.combo_matricula_cuotas.pack(anchor="w", padx=5, pady=5)

        self.scroll_cuotas = ctk.CTkScrollableFrame(self.tab_cuotas)
        self.scroll_cuotas.pack(fill="both", expand=True, padx=5, pady=5)

        self._cargar_combo_matriculas()

    def _cargar_matriculas(self, busqueda=""):
        for widget in self.scroll_matriculas.winfo_children():
            widget.destroy()

        matriculas = matricula_controller.listar_matriculas_activas()

        if busqueda:
            busqueda_lower = busqueda.lower()
            matriculas = [
                m for m in matriculas
                if busqueda_lower in (m.get("dni", "") or "").lower()
                or busqueda_lower in (m.get("nombres", "") or "").lower()
                or busqueda_lower in (m.get("apellidos", "") or "").lower()
            ]

        if not matriculas:
            ctk.CTkLabel(
                self.scroll_matriculas, text="No hay matrículas activas",
                text_color="gray",
            ).pack(pady=20)
            self.label_status.configure(text="Total: 0")
            return

        for mat in matriculas:
            self._crear_card(mat)

        self.label_status.configure(text=f"Total: {len(matriculas)} matrícula(s)")

    def _on_busqueda_cambiar(self, event):
        busqueda = self.entry_busqueda.get().strip()
        self._cargar_matriculas(busqueda)

    def _crear_card(self, mat):
        card = ctk.CTkFrame(self.scroll_matriculas)
        card.pack(fill="x", padx=5, pady=3)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=10, pady=8)

        nombre = f"{mat.get('nombres', '')} {mat.get('apellidos', '')}"
        ctk.CTkLabel(
            info, text=nombre,
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            info,
            text=f"DNI: {mat.get('dni', '')} | Tarifa: {mat.get('tarifa_nombre', '')} | "
                 f"Montos: S/{mat.get('tarifa_monto', 0):.2f}",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(anchor="w")

        ctk.CTkLabel(
            info,
            text=f"Inicio: {mat.get('fecha_inicio', '')} | Vencimiento: día {mat.get('dia_vencimiento', 1)}",
            font=ctk.CTkFont(size=11), text_color="gray",
        ).pack(anchor="w")

        botones = ctk.CTkFrame(card, fg_color="transparent")
        botones.pack(side="right", padx=5, pady=5)

        ctk.CTkButton(
            botones, text="Ver Cuotas", width=90, height=28,
            command=lambda m=mat: self._ver_cuotas(m),
        ).pack(side="left", padx=2)

    def _nueva_matricula(self):
        self._cargar_combo_estudiantes()
        self._cargar_combo_tarifas()
        self._cargar_combo_becas()
        self.tabview.set("Registrar")

    def _cargar_combo_estudiantes(self):
        estudiantes = estudiante_controller.listar_estudiantes(activo=1, estado=["ACTIVO", "REINGRESANTE"])
        nombres = [f"{e.get('nombres', '')} {e.get('apellidos', '')}" for e in estudiantes]
        self.combo_estudiante.configure(values=nombres if nombres else ["Sin estudiantes"])
        self._estudiantes_map = {n: e for n, e in zip(nombres, estudiantes)}

    def _on_estudiante_changed(self, selection):
        est = self._estudiantes_map.get(selection)
        if not est:
            return
        fecha_nac = est.get("fecha_nacimiento", "")
        if not fecha_nac:
            return
        id_tarifa_sugerida = matricula_controller.obtener_tarifa_sugerida_por_edad(fecha_nac)
        if not id_tarifa_sugerida:
            return
        for nombre, tid in self._tarifas_map.items():
            if tid == id_tarifa_sugerida:
                self.combo_tarifa.set(nombre)
                break

    def _cargar_combo_tarifas(self):
        tarifas = matricula_controller.listar_tarifas_activas()
        nombres = [f"{t.get('categoria_nombre', '')} - {t['nombre']} (S/{t['monto']:.2f})" for t in tarifas]
        self.combo_tarifa.configure(values=nombres if nombres else ["Sin tarifas"])
        self._tarifas_map = {n: t["id_tarifa"] for n, t in zip(nombres, tarifas)}

    def _cargar_combo_becas(self):
        becas = matricula_controller.listar_becas()
        nombres = ["Ninguna"] + [f"{b['nombre']} ({b['tipo']} {b['valor']})" for b in becas]
        self.combo_beca.configure(values=nombres)
        self._becas_map = {n: b["id_beca"] for n, b in zip(nombres[1:], becas)}

    def _registrar_matricula(self):
        est_selection = self.combo_estudiante.get()
        est = self._estudiantes_map.get(est_selection)
        id_est = est["id_estudiante"] if est else None
        if not id_est:
            self.label_form_status.configure(text="Seleccione un estudiante", text_color="red")
            return

        tarifa_selection = self.combo_tarifa.get()
        id_tarifa = self._tarifas_map.get(tarifa_selection)
        if not id_tarifa:
            self.label_form_status.configure(text="Seleccione una tarifa", text_color="red")
            return

        data = {
            "id_estudiante": id_est,
            "id_tarifa": id_tarifa,
            "monto_pactado": self.entry_monto_pactado.get().strip() or None,
            "dia_vencimiento": self.entry_dia_venc.get().strip() or "1",
        }

        beca_selection = self.combo_beca.get()
        if beca_selection != "Ninguna" and beca_selection in self._becas_map:
            data["becas"] = [{"id_beca": self._becas_map[beca_selection]}]

        exito, msg, id_mat = matricula_controller.crear_matricula(data)

        if exito:
            self.label_form_status.configure(text=msg, text_color="green")
            self._cargar_matriculas()
            self._cargar_combo_matriculas()
            self.tabview.set("Matrículas")
        else:
            self.label_form_status.configure(text=msg, text_color="red")

    def _ver_cuotas(self, mat):
        self.tabview.set("Cuotas")
        self._cargar_combo_matriculas()
        id_str = f"ID:{mat['id_matricula']}"
        for key, val in self._matriculas_map.items():
            if val == mat["id_matricula"]:
                self.combo_matricula_cuotas.set(key)
                self._cargar_cuotas(key)
                break

    def _cargar_combo_matriculas(self):
        matriculas = matricula_controller.listar_matriculas_activas()
        nombres = [f"{m.get('nombres', '')} {m.get('apellidos', '')} - {m.get('tarifa_nombre', '')}" for m in matriculas]
        self.combo_matricula_cuotas.configure(values=nombres if nombres else ["Sin matrículas"])
        self._matriculas_map = {n: m["id_matricula"] for n, m in zip(nombres, matriculas)}

    def _cargar_cuotas(self, selection):
        for widget in self.scroll_cuotas.winfo_children():
            widget.destroy()

        id_mat = self._matriculas_map.get(selection)
        if not id_mat:
            return

        cuotas = matricula_controller.obtener_cuotas_por_matricula(id_mat)

        if not cuotas:
            ctk.CTkLabel(
                self.scroll_cuotas, text="Sin cuotas registradas",
                text_color="gray",
            ).pack(pady=10)
            return

        for cuota in cuotas:
            card = ctk.CTkFrame(self.scroll_cuotas)
            card.pack(fill="x", padx=5, pady=3)

            color = {"PENDIENTE": "gray", "PARCIAL": "orange",
                     "PAGADO": "green", "VENCIDO": "red"}.get(cuota["estado"], "gray")

            ctk.CTkLabel(
                card,
                text=f"{cuota['periodo']} | S/{cuota['monto_total']:.2f} | "
                     f"Pagado: S/{cuota['monto_pagado']:.2f} | Saldo: S/{cuota['saldo']:.2f}",
                font=ctk.CTkFont(size=12),
            ).pack(side="left", padx=10, pady=8)

            ctk.CTkLabel(
                card, text=cuota["estado"], text_color=color,
                font=ctk.CTkFont(size=12, weight="bold"),
            ).pack(side="right", padx=10)
