import customtkinter as ctk
from controllers import estudiante_controller


class EstudianteView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._crear_widgets()
        self._cargar_estudiantes()

    def _crear_widgets(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_lista = self.tabview.add("Estudiantes")
        self.tab_form = self.tabview.add("Registrar / Editar")
        self.tab_apoderados = self.tabview.add("Apoderados")

        self._crear_tab_lista()
        self._crear_tab_formulario()
        self._crear_tab_apoderados()

    def _crear_tab_lista(self):
        header = ctk.CTkFrame(self.tab_lista, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            header, text="Lista de Estudiantes",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            header, text="+ Nuevo", width=100,
            command=self._nuevo_estudiante,
        ).pack(side="right")

        filtros = ctk.CTkFrame(self.tab_lista, fg_color="transparent")
        filtros.pack(fill="x", padx=5, pady=5)

        self.filtro_estado = ctk.CTkSegmentedButton(
            filtros, values=["Todos", "Activos", "Retirados"],
            command=self._filtrar,
        )
        self.filtro_estado.set("Todos")
        self.filtro_estado.pack(side="left")

        self.scroll_estudiantes = ctk.CTkScrollableFrame(self.tab_lista)
        self.scroll_estudiantes.pack(fill="both", expand=True, padx=5, pady=5)

        self.label_status = ctk.CTkLabel(self.tab_lista, text="", font=ctk.CTkFont(size=11))
        self.label_status.pack(pady=3)

    def _crear_tab_formulario(self):
        scroll = ctk.CTkScrollableFrame(self.tab_form)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll, text="Datos del Estudiante",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", pady=(0, 10))

        self.entry_dni = ctk.CTkEntry(scroll, placeholder_text="DNI (8 dígitos)", width=300)
        self.entry_dni.pack(anchor="w", pady=3)

        self.entry_nombres = ctk.CTkEntry(scroll, placeholder_text="Nombres", width=400)
        self.entry_nombres.pack(anchor="w", pady=3)

        self.entry_apellidos = ctk.CTkEntry(scroll, placeholder_text="Apellidos", width=400)
        self.entry_apellidos.pack(anchor="w", pady=3)

        row1 = ctk.CTkFrame(scroll, fg_color="transparent")
        row1.pack(fill="x", anchor="w", pady=3)

        ctk.CTkLabel(row1, text="Fecha nacimiento:").pack(side="left", padx=(0, 5))
        self.entry_fecha_nac = ctk.CTkEntry(row1, placeholder_text="YYYY-MM-DD", width=150)
        self.entry_fecha_nac.pack(side="left")

        ctk.CTkLabel(row1, text="Sexo:").pack(side="left", padx=(20, 5))
        self.combo_sexo = ctk.CTkComboBox(row1, values=["", "M", "F"], width=80)
        self.combo_sexo.set("")
        self.combo_sexo.pack(side="left")

        self.entry_direccion = ctk.CTkEntry(scroll, placeholder_text="Dirección", width=400)
        self.entry_direccion.pack(anchor="w", pady=3)

        row2 = ctk.CTkFrame(scroll, fg_color="transparent")
        row2.pack(fill="x", anchor="w", pady=3)

        ctk.CTkLabel(row2, text="Teléfono:").pack(side="left", padx=(0, 5))
        self.entry_telefono = ctk.CTkEntry(row2, placeholder_text="Teléfono", width=150)
        self.entry_telefono.pack(side="left")

        ctk.CTkLabel(row2, text="Correo:").pack(side="left", padx=(20, 5))
        self.entry_correo = ctk.CTkEntry(row2, placeholder_text="Correo", width=200)
        self.entry_correo.pack(side="left")

        self.label_form_status = ctk.CTkLabel(scroll, text="", font=ctk.CTkFont(size=12))
        self.label_form_status.pack(anchor="w", pady=5)

        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(anchor="w", pady=10)

        self.btn_guardar = ctk.CTkButton(
            btn_frame, text="Guardar", width=120,
            command=self._guardar_estudiante,
        )
        self.btn_guardar.pack(side="left", padx=5)

        self.btn_cancelar = ctk.CTkButton(
            btn_frame, text="Cancelar", width=120, fg_color="gray",
            command=self._cancelar_formulario,
        )
        self.btn_cancelar.pack(side="left", padx=5)

        self._id_estudiante_editando = None

    def _crear_tab_apoderados(self):
        header = ctk.CTkFrame(self.tab_apoderados, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            header, text="Apoderados por Estudiante",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            header, text="+ Asociar", width=110,
            command=self._asociar_apoderado,
        ).pack(side="right")

        self.combo_estudiante = ctk.CTkComboBox(
            self.tab_apoderados, values=["Seleccionar estudiante..."],
            width=350, command=self._cargar_apoderados_estudiante,
        )
        self.combo_estudiante.set("Seleccionar estudiante...")
        self.combo_estudiante.pack(anchor="w", padx=5, pady=5)

        self.scroll_apoderados = ctk.CTkScrollableFrame(self.tab_apoderados)
        self.scroll_apoderados.pack(fill="both", expand=True, padx=5, pady=5)

        self._cargar_combo_estudiantes()

    def _cargar_estudiantes(self, activo=None, estado=None):
        for widget in self.scroll_estudiantes.winfo_children():
            widget.destroy()

        estudiantes = estudiante_controller.listar_estudiantes(activo=activo, estado=estado)

        if not estudiantes:
            ctk.CTkLabel(
                self.scroll_estudiantes, text="No hay estudiantes registrados",
                text_color="gray",
            ).pack(pady=20)
            self.label_status.configure(text="Total: 0")
            return

        for est in estudiantes:
            self._crear_card_estudiante(est)

        self.label_status.configure(text=f"Total: {len(estudiantes)} estudiante(s)")

    def _crear_card_estudiante(self, est):
        card = ctk.CTkFrame(self.scroll_estudiantes)
        card.pack(fill="x", padx=5, pady=3)

        estado = est.get("estado", "ACTIVO")
        color_estado = "green" if estado == "ACTIVO" else ("orange" if estado == "REINGRESANTE" else "red")

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=10, pady=8)

        nombre = f"{est.get('nombres', '')} {est.get('apellidos', '')}"
        ctk.CTkLabel(
            info, text=nombre,
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            info, text=f"DNI: {est.get('dni', '')}  |  Estado: {estado}",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(anchor="w")

        botones = ctk.CTkFrame(card, fg_color="transparent")
        botones.pack(side="right", padx=5, pady=5)

        ctk.CTkButton(
            botones, text="Editar", width=70, height=28,
            command=lambda e=est: self._editar_estudiante(e),
        ).pack(side="left", padx=2)

        if estado == "ACTIVO":
            ctk.CTkButton(
                botones, text="Retirar", width=70, height=28,
                fg_color="red", hover_color="darkred",
                command=lambda e=est: self._retirar(e),
            ).pack(side="left", padx=2)
        elif estado == "RETIRADO":
            ctk.CTkButton(
                botones, text="Reingreso", width=80, height=28,
                fg_color="orange", hover_color="darkorange",
                command=lambda e=est: self._reingreso(e),
            ).pack(side="left", padx=2)

    def _nuevo_estudiante(self):
        self._limpiar_formulario()
        self.tabview.set("Registrar / Editar")

    def _editar_estudiante(self, est):
        self._limpiar_formulario()
        self._id_estudiante_editando = est["id_estudiante"]

        estudiante = estudiante_controller.obtener_estudiante(est["id_estudiante"])
        if estudiante:
            self.entry_dni.insert(0, estudiante.get("dni", ""))
            self.entry_nombres.insert(0, estudiante.get("nombres", ""))
            self.entry_apellidos.insert(0, estudiante.get("apellidos", ""))
            self.entry_fecha_nac.insert(0, estudiante.get("fecha_nacimiento", "") or "")
            self.combo_sexo.set(estudiante.get("sexo", "") or "")
            self.entry_direccion.insert(0, estudiante.get("direccion", "") or "")
            self.entry_telefono.insert(0, estudiante.get("telefono", "") or "")
            self.entry_correo.insert(0, estudiante.get("correo", "") or "")

        self.tabview.set("Registrar / Editar")

    def _guardar_estudiante(self):
        data = {
            "dni": self.entry_dni.get().strip(),
            "nombres": self.entry_nombres.get().strip(),
            "apellidos": self.entry_apellidos.get().strip(),
            "fecha_nacimiento": self.entry_fecha_nac.get().strip(),
            "sexo": self.combo_sexo.get(),
            "direccion": self.entry_direccion.get().strip(),
            "telefono": self.entry_telefono.get().strip(),
            "correo": self.entry_correo.get().strip(),
        }

        if self._id_estudiante_editando:
            exito, msg = estudiante_controller.editar_estudiante(
                self._id_estudiante_editando, data,
            )
        else:
            exito, msg, _ = estudiante_controller.crear_estudiante(data)

        if exito:
            self.label_form_status.configure(text=msg, text_color="green")
            self._limpiar_formulario()
            self._cargar_estudiantes()
            self._cargar_combo_estudiantes()
            self.tabview.set("Estudiantes")
        else:
            self.label_form_status.configure(text=msg, text_color="red")

    def _cancelar_formulario(self):
        self._limpiar_formulario()
        self.tabview.set("Estudiantes")

    def _limpiar_formulario(self):
        self._id_estudiante_editando = None
        self.entry_dni.delete(0, "end")
        self.entry_nombres.delete(0, "end")
        self.entry_apellidos.delete(0, "end")
        self.entry_fecha_nac.delete(0, "end")
        self.combo_sexo.set("")
        self.entry_direccion.delete(0, "end")
        self.entry_telefono.delete(0, "end")
        self.entry_correo.delete(0, "end")
        self.label_form_status.configure(text="")

    def _retirar(self, est):
        exito, msg = estudiante_controller.registrar_retiro(est["id_estudiante"])
        if exito:
            self._cargar_estudiantes()
            self._cargar_combo_estudiantes()

    def _reingreso(self, est):
        exito, msg = estudiante_controller.registrar_reingreso(est["id_estudiante"])
        if exito:
            self._cargar_estudiantes()
            self._cargar_combo_estudiantes()

    def _filtrar(self, valor):
        if valor == "Activos":
            self._cargar_estudiantes(activo=1)
        elif valor == "Retirados":
            self._cargar_estudiantes(estado="RETIRADO")
        else:
            self._cargar_estudiantes()

    def _cargar_combo_estudiantes(self):
        estudiantes = estudiante_controller.listar_estudiantes(activo=1)
        nombres = [f"{e.get('nombres', '')} {e.get('apellidos', '')} (ID:{e['id_estudiante']})" for e in estudiantes]
        self.combo_estudiante.configure(values=nombres if nombres else ["Sin estudiantes"])
        self._estudiantes_map = {n: e["id_estudiante"] for n, e in zip(nombres, estudiantes)}

    def _cargar_apoderados_estudiante(self, selection):
        for widget in self.scroll_apoderados.winfo_children():
            widget.destroy()

        id_est = self._estudiantes_map.get(selection)
        if not id_est:
            return

        apoderados = estudiante_controller.obtener_apoderados_por_estudiante(id_est)

        if not apoderados:
            ctk.CTkLabel(
                self.scroll_apoderados, text="Sin apoderados asociados",
                text_color="gray",
            ).pack(pady=10)
            return

        for ap in apoderados:
            card = ctk.CTkFrame(self.scroll_apoderados)
            card.pack(fill="x", padx=5, pady=3)

            principal_text = " (PRINCIPAL)" if ap.get("es_principal") else ""
            ctk.CTkLabel(
                card,
                text=f"{ap.get('nombres', '')} {ap.get('apellidos', '')} - {ap.get('parentesco', '')}{principal_text}",
                font=ctk.CTkFont(size=13),
            ).pack(side="left", padx=10, pady=8)

            ctk.CTkButton(
                card, text="Quitar", width=70, height=26,
                fg_color="red", hover_color="darkred",
                command=lambda a=ap, e=id_est: self._desasociar(e, a["id_apoderado"]),
            ).pack(side="right", padx=5, pady=5)

    def _asociar_apoderado(self):
        selection = self.combo_estudiante.get()
        id_est = self._estudiantes_map.get(selection)
        if not id_est:
            return

        dialog = ctk.CTkInputDialog(
            text="Ingrese DNI del apoderado:", title="DNI del Apoderado",
        )
        dni = dialog.get_input()
        if not dni:
            return

        from controllers import persona_controller
        persona = persona_controller.buscar_por_dni(dni)
        if not persona:
            dialog2 = ctk.CTkInputDialog(
                text="Apoderado no encontrado. Nombres:", title="Registrar Apoderado",
            )
            nombres = dialog2.get_input()
            if not nombres:
                return

            dialog3 = ctk.CTkInputDialog(
                text="Apellidos:", title="Apellidos",
            )
            apellidos = dialog3.get_input()
            if not apellidos:
                return

            dialog4 = ctk.CTkInputDialog(
                text="Parentesco:", title="Parentesco",
            )
            parentesco = dialog4.get_input()
            if not parentesco:
                return

            exito, msg, id_apoderado = estudiante_controller.crear_apoderado({
                "dni": dni, "nombres": nombres, "apellidos": apellidos,
                "parentesco": parentesco,
            })
            if not exito:
                ctk.CTkLabel(self.scroll_apoderados, text=msg, text_color="red").pack(pady=5)
                return
        else:
            exito2, msg2, id_apoderado = estudiante_controller.crear_apoderado({
                "dni": dni, "parentesco": "No especificado",
            })

        if not id_apoderado:
            apo = estudiante_controller.obtener_apoderado_por_persona(persona["id_persona"] if persona else None)
            if apo:
                id_apoderado = apo["id_apoderado"]
            else:
                return

        tiene_principal = estudiante_controller.obtener_apoderados_por_estudiante(id_est)
        es_principal = len(tiene_principal) == 0

        exito, msg = estudiante_controller.asociar_apoderado(id_est, id_apoderado, es_principal)
        if exito:
            self._cargar_apoderados_estudiante(selection)

    def _desasociar(self, id_est, id_apoderado):
        exito, msg = estudiante_controller.desasociar_apoderado(id_est, id_apoderado)
        if exito:
            selection = self.combo_estudiante.get()
            self._cargar_apoderados_estudiante(selection)
