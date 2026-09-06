import customtkinter as ctk
from controllers import dashboard_controller

try:
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._crear_widgets()
        self._cargar_indicadores()

    def _crear_widgets(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=15, pady=(15, 5))

        self.titulo_label = ctk.CTkLabel(
            self.header, text="📊  Dashboard",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#3D1559",  # Morado oscuro
        )
        self.titulo_label.pack(side="left")

        self.btn_volver = ctk.CTkButton(
            self.header, text="Volver", width=100,
            command=self._mostrar_cards, fg_color="gray",
        )

        self.btn_actualizar = ctk.CTkButton(
            self.header, text="Actualizar", width=100,
            command=self._cargar_indicadores,
        )
        self.btn_actualizar.pack(side="right")

        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=15, pady=5)

        self.detalle_frame = ctk.CTkScrollableFrame(self)
        self.detalle_frame.pack(fill="both", expand=True, padx=15, pady=5)

    def _cargar_indicadores(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        for widget in self.detalle_frame.winfo_children():
            widget.destroy()

        data = dashboard_controller.obtener_indicadores()

        self.btn_volver.pack_forget()
        self.btn_actualizar.pack(side="right")
        self.titulo_label.configure(text="Dashboard")

        row1 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)

        self._crear_card(row1, "Alumnos Activos", str(data["alumnos_activos"]), "#7C3AED",
                         lambda: self._mostrar_detalle("alumnos"))
        self._crear_card(row1, "Cuotas Vencidas", str(data["cuotas_vencidas"]), "#DC2626",
                         lambda: self._mostrar_detalle("vencidas"))
        self._crear_card(row1, "Por Vencer", str(data["cuotas_por_vencer"]), "#F59E0B",
                         lambda: self._mostrar_detalle("por_vencer"))

        row2 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)

        self._crear_card(row2, "Pagos Hoy", str(data["pagos_hoy"]), "#22C55E",
                         lambda: self._mostrar_detalle("pagos_hoy"))
        self._crear_card(row2, "Ingresos Hoy", f"S/{data['ingresos_hoy']:.2f}", "#22C55E",
                         lambda: self._mostrar_detalle("ingresos_hoy"))
        self._crear_card(row2, "Ingresos Mes", f"S/{data['ingresos_mes']:.2f}", "#6B21A8",
                         lambda: self._mostrar_detalle("ingresos_mes"))

        row3 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)

        self._crear_card(row3, "Monto Vencido", f"S/{data['monto_vencido']:.2f}", "#DC2626",
                         lambda: self._mostrar_detalle("monto_vencido"))
        self._crear_card(row3, "Monto por Vencer", f"S/{data['monto_por_vencer']:.2f}", "#F59E0B",
                         lambda: self._mostrar_detalle("monto_por_vencer"))
        self._crear_card(row3, "Stock Bajo", str(data["stock_bajo"]), "#F59E0B",
                         lambda: self._mostrar_detalle("stock"))

        row4 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)

        self._crear_card(row4, "Ventas Mes", f"S/{data.get('ingresos_ventas_mes',0):.2f}", "#7C3AED",
                         lambda: self._mostrar_detalle("ventas_mes"))
        self._crear_card(row4, "Egresos Mes", f"S/{data.get('egresos_mes',0):.2f}", "#DC2626",
                         lambda: self._mostrar_detalle("egresos_mes"))
        self._crear_card(row4, "Neto Mes", f"S/{data.get('neto_mes',0):.2f}", "#22C55E" if data.get('neto_mes',0) >=0 else "#DC2626",
                         lambda: self._mostrar_detalle("neto_mes"))

        row5 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row5.pack(fill="x", pady=5)

        self._crear_card(row5, "Nuevos Mes", str(data.get("nuevos_mes",0)), "#22C55E",
                         lambda: self._mostrar_detalle("nuevos_mes"))
        self._crear_card(row5, "Antiguos Mes", str(data.get("antiguos_mes",0)), "#6B21A8",
                         lambda: self._mostrar_detalle("antiguos_mes"))
        self._crear_card(row5, "Total Matrículas Mes", str(data.get("matriculas_mes",0)), "#3D1559",
                         lambda: self._mostrar_detalle("matriculas_mes"))

        for widget in self.detalle_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.detalle_frame,
            text="Haga clic en cualquier card para ver el detalle",
            font=ctk.CTkFont(size=14), text_color="gray",
        ).pack(expand=True)

    def _crear_card(self, parent, titulo, valor, color, comando):
        card = ctk.CTkButton(
            parent, width=200, height=80,
            fg_color="white", hover_color="#f0f0f0",
            command=comando,
        )
        card.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        card.pack_propagate(False)

        frame_interno = ctk.CTkFrame(card, fg_color="transparent")
        frame_interno.pack(expand=True)

        ctk.CTkLabel(
            frame_interno, text=titulo,
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(pady=(10, 0))

        ctk.CTkLabel(
            frame_interno, text=valor,
            font=ctk.CTkFont(size=22, weight="bold"), text_color=color,
        ).pack(pady=(0, 10))

    def _mostrar_detalle(self, tipo):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        for widget in self.detalle_frame.winfo_children():
            widget.destroy()

        self.btn_actualizar.pack_forget()
        self.btn_volver.pack(side="right")

        titulos = {
            "alumnos": "Alumnos Activos",
            "vencidas": "Cuotas Vencidas",
            "por_vencer": "Cuotas por Vencer",
            "pagos_hoy": "Pagos de Hoy",
            "ingresos_hoy": "Ingresos de Hoy",
            "ingresos_mes": "Ingresos del Mes",
            "monto_vencido": "Monto Vencido",
            "monto_por_vencer": "Monto por Vencer",
            "stock": "Productos con Stock Bajo",
            "ventas_mes": "Ventas del Mes (Uniformes/Tienda)",
            "egresos_mes": "Egresos del Mes",
            "neto_mes": "Neto del Mes (Ingresos - Egresos)",
            "nuevos_mes": "Alumnos Nuevos del Mes",
            "antiguos_mes": "Alumnos Antiguos (Matrículas)",
            "matriculas_mes": "Matrículas del Mes",
        }
        self.titulo_label.configure(text=titulos.get(tipo, "Detalle"))

        if tipo == "alumnos":
            self._detalle_alumnos()
        elif tipo == "vencidas":
            self._detalle_cuotas(dashboard_controller.listar_cuotas_vencidas(), "vencida")
        elif tipo == "por_vencer":
            self._detalle_cuotas(dashboard_controller.listar_cuotas_por_vencer(), "por vencer")
        elif tipo == "pagos_hoy":
            self._detalle_pagos(dashboard_controller.listar_pagos_hoy())
        elif tipo == "ingresos_hoy":
            self._detalle_ingresos_hoy()
        elif tipo == "ingresos_mes":
            self._detalle_ingresos_mes()
        elif tipo == "monto_vencido":
            self._detalle_monto(dashboard_controller.listar_monto_vencido(), "vencido")
        elif tipo == "monto_por_vencer":
            self._detalle_monto(dashboard_controller.listar_monto_por_vencer(), "por vencer")
        elif tipo == "stock":
            self._detalle_stock()
        elif tipo == "ventas_mes":
            self._detalle_ventas_mes()
        elif tipo == "egresos_mes":
            self._detalle_egresos_mes()
        elif tipo == "neto_mes":
            self._detalle_neto_mes()
        elif tipo == "nuevos_mes":
            self._detalle_nuevos_mes()
        elif tipo == "antiguos_mes":
            self._detalle_antiguos_mes()
        elif tipo == "matriculas_mes":
            self._detalle_matriculas_mes()

    def _mostrar_cards(self):
        self._cargar_indicadores()

    def _detalle_alumnos(self):
        alumnos = dashboard_controller.listar_alumnos_activos()

        ctk.CTkLabel(
            self.detalle_frame,
            text=f"Total: {len(alumnos)} alumnos activos",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(10, 5))

        if not alumnos:
            ctk.CTkLabel(self.detalle_frame, text="No hay alumnos activos").pack(pady=10)
            return

        header = ctk.CTkFrame(self.detalle_frame, fg_color="#DDD6E5")  # Borde morado claro
        header.pack(fill="x", padx=5, pady=2)

        for col, (texto, ancho) in enumerate([
            ("DNI", 80), ("Nombre", 200), ("Edad", 60), ("Teléfono", 100)
        ]):
            ctk.CTkLabel(
                header, text=texto, width=ancho,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#3D1559",  # Morado oscuro
            ).grid(row=0, column=col, padx=5, pady=5)

        for i, alumno in enumerate(alumnos[:50]):
            row = ctk.CTkFrame(self.detalle_frame)
            row.pack(fill="x", padx=5, pady=1)

            ctk.CTkLabel(row, text=str(alumno.get("dni", "")), width=80,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=5, pady=3)
            ctk.CTkLabel(row, text=f"{alumno.get('nombres', '')} {alumno.get('apellidos', '')}",
                         width=200, font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(alumno.get("edad", "")), width=60,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(alumno.get("telefono", "")), width=100,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=5, pady=3)

        if len(alumnos) > 50:
            ctk.CTkLabel(
                self.detalle_frame,
                text=f"Mostrando 50 de {len(alumnos)} alumnos",
                text_color="gray",
            ).pack(pady=5)

    def _detalle_cuotas(self, cuotas, tipo):
        ctk.CTkLabel(
            self.detalle_frame,
            text=f"Total: {len(cuotas)} cuotas {tipo}",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(10, 5))

        if not cuotas:
            ctk.CTkLabel(self.detalle_frame, text=f"No hay cuotas {tipo}").pack(pady=10)
            return

        header = ctk.CTkFrame(self.detalle_frame, fg_color="#DDD6E5")  # Morado claro
        header.pack(fill="x", padx=5, pady=2)

        for col, (texto, ancho) in enumerate([
            ("Estudiante", 200), ("DNI", 80), ("Período", 80),
            ("Saldo", 80), ("Vencimiento", 100)
        ]):
            ctk.CTkLabel(
                header, text=texto, width=ancho,
                font=ctk.CTkFont(size=12, weight="bold"),
            ).grid(row=0, column=col, padx=5, pady=5)

        for i, cuota in enumerate(cuotas[:30]):
            row = ctk.CTkFrame(self.detalle_frame)
            row.pack(fill="x", padx=5, pady=1)

            nombre = f"{cuota.get('nombres', '')} {cuota.get('apellidos', '')}"
            ctk.CTkLabel(row, text=nombre, width=200,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(cuota.get("dni", "")), width=80,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(cuota.get("periodo", "")), width=80,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=5, pady=3)
            ctk.CTkLabel(row, text=f"S/{cuota.get('saldo', 0):.2f}", width=80,
                         font=ctk.CTkFont(size=11), text_color="red").grid(row=0, column=3, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(cuota.get("fecha_vencimiento", "")), width=100,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=4, padx=5, pady=3)

        if len(cuotas) > 30:
            ctk.CTkLabel(
                self.detalle_frame,
                text=f"Mostrando 30 de {len(cuotas)} cuotas",
                text_color="gray",
            ).pack(pady=5)

    def _detalle_pagos(self, pagos):
        ctk.CTkLabel(
            self.detalle_frame,
            text=f"Total: {len(pagos)} pagos realizados hoy",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(10, 5))

        if not pagos:
            ctk.CTkLabel(self.detalle_frame, text="No hay pagos registrados hoy").pack(pady=10)
            return

        header = ctk.CTkFrame(self.detalle_frame, fg_color="#DDD6E5")  # Morado claro
        header.pack(fill="x", padx=5, pady=2)

        for col, (texto, ancho) in enumerate([
            ("N° Recibo", 120), ("Monto", 80), ("Método", 100), ("Fecha", 100)
        ]):
            ctk.CTkLabel(
                header, text=texto, width=ancho,
                font=ctk.CTkFont(size=12, weight="bold"),
            ).grid(row=0, column=col, padx=5, pady=5)

        for pago in pagos:
            row = ctk.CTkFrame(self.detalle_frame)
            row.pack(fill="x", padx=5, pady=1)

            ctk.CTkLabel(row, text=str(pago.get("numero_recibo", "")), width=120,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=5, pady=3)
            ctk.CTkLabel(row, text=f"S/{pago.get('monto_total', 0):.2f}", width=80,
                         font=ctk.CTkFont(size=11), text_color="green").grid(row=0, column=1, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(pago.get("metodo_pago", "")), width=100,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(pago.get("fecha_pago", "")), width=100,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=5, pady=3)

    def _detalle_ingresos_hoy(self):
        pagos = dashboard_controller.listar_pagos_hoy()
        total = sum(p.get("monto_total", 0) for p in pagos)

        ctk.CTkLabel(
            self.detalle_frame,
            text=f"Total: S/{total:.2f} en {len(pagos)} transacciones",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(10, 5))

        if not pagos:
            ctk.CTkLabel(self.detalle_frame, text="No hay ingresos hoy").pack(pady=10)
            return

        if MATPLOTLIB_DISPONIBLE:
            self._crear_grafico_barras_simple(
                [f"Pago {i+1}" for i in range(len(pagos))],
                [p.get("monto_total", 0) for p in pagos],
                "Ingresos por Transacción",
            )

    def _detalle_ingresos_mes(self):
        datos = dashboard_controller.obtener_ingresos_por_dia_mes()
        total = sum(d.get("monto", 0) for d in datos)

        ctk.CTkLabel(
            self.detalle_frame,
            text=f"Total: S/{total:.2f} en {len(datos)} días con actividad",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(10, 5))

        if not datos:
            ctk.CTkLabel(self.detalle_frame, text="No hay ingresos este mes").pack(pady=10)
            return

        if MATPLOTLIB_DISPONIBLE:
            self._crear_grafico_barras_simple(
                [d.get("dia", "")[-5:] for d in datos],
                [d.get("monto", 0) for d in datos],
                "Ingresos por Día del Mes",
            )

        header = ctk.CTkFrame(self.detalle_frame, fg_color="#DDD6E5")  # Morado claro
        header.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(header, text="Fecha", width=120,
                     font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(header, text="Monto", width=100,
                     font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=1, padx=5, pady=5)

        for d in datos:
            row = ctk.CTkFrame(self.detalle_frame)
            row.pack(fill="x", padx=5, pady=1)

            ctk.CTkLabel(row, text=str(d.get("dia", "")), width=120,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=5, pady=3)
            ctk.CTkLabel(row, text=f"S/{d.get('monto', 0):.2f}", width=100,
                         font=ctk.CTkFont(size=11), text_color="green").grid(row=0, column=1, padx=5, pady=3)

    def _detalle_monto(self, cuotas, tipo):
        total = sum(c.get("saldo", 0) for c in cuotas)

        ctk.CTkLabel(
            self.detalle_frame,
            text=f"Total: S/{total:.2f} en {len(cuotas)} cuotas {tipo}",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(10, 5))

        if not cuotas:
            ctk.CTkLabel(self.detalle_frame, text=f"No hay cuotas {tipo}").pack(pady=10)
            return

        if MATPLOTLIB_DISPONIBLE and len(cuotas) > 0:
            nombres = [f"{c.get('nombres', '')[:10]} {c.get('apellidos', '')[:10]}" for c in cuotas[:10]]
            saldos = [c.get("saldo", 0) for c in cuotas[:10]]
            self._crear_grafico_barras_simple(nombres, saldos, f"Saldo {tipo} por Estudiante")

        header = ctk.CTkFrame(self.detalle_frame, fg_color="#DDD6E5")  # Morado claro
        header.pack(fill="x", padx=5, pady=2)

        for col, (texto, ancho) in enumerate([
            ("Estudiante", 200), ("DNI", 80), ("Saldo", 100)
        ]):
            ctk.CTkLabel(
                header, text=texto, width=ancho,
                font=ctk.CTkFont(size=12, weight="bold"),
            ).grid(row=0, column=col, padx=5, pady=5)

        for c in cuotas[:20]:
            row = ctk.CTkFrame(self.detalle_frame)
            row.pack(fill="x", padx=5, pady=1)

            nombre = f"{c.get('nombres', '')} {c.get('apellidos', '')}"
            ctk.CTkLabel(row, text=nombre, width=200,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(c.get("dni", "")), width=80,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=5, pady=3)
            ctk.CTkLabel(row, text=f"S/{c.get('saldo', 0):.2f}", width=100,
                         font=ctk.CTkFont(size=11), text_color="red").grid(row=0, column=2, padx=5, pady=3)

        if len(cuotas) > 20:
            ctk.CTkLabel(
                self.detalle_frame,
                text=f"Mostrando 20 de {len(cuotas)} cuotas",
                text_color="gray",
            ).pack(pady=5)

    def _detalle_ventas_mes(self):
        from datetime import date
        hoy = date.today()
        ini = hoy.replace(day=1).isoformat()
        try:
            from controllers import venta_controller
            ventas = venta_controller.listar_ventas(ini, hoy.isoformat())
            total = sum(v.get("monto_total",0) for v in ventas)
            ctk.CTkLabel(self.detalle_frame, text=f"Ventas mes: S/{total:.2f} en {len(ventas)} ventas", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10,5))
            for v in ventas[:20]:
                row = ctk.CTkFrame(self.detalle_frame)
                row.pack(fill="x", padx=5, pady=1)
                ctk.CTkLabel(row, text=f"{v.get('tipo_venta','')} {v.get('numero_recibo','')} S/{v.get('monto_total',0):.2f}", font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
        except Exception as e:
            ctk.CTkLabel(self.detalle_frame, text=f"Error: {e}").pack()

    def _detalle_egresos_mes(self):
        from datetime import date
        hoy = date.today()
        ini = hoy.replace(day=1).isoformat()
        try:
            from controllers import egreso_controller
            egresos = egreso_controller.listar_egresos(ini, hoy.isoformat())
            total = sum(e.get("monto",0) for e in egresos)
            ctk.CTkLabel(self.detalle_frame, text=f"Egresos mes: S/{total:.2f} en {len(egresos)}", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10,5))
            for e in egresos[:20]:
                row = ctk.CTkFrame(self.detalle_frame)
                row.pack(fill="x", padx=5, pady=1)
                ctk.CTkLabel(row, text=f"{e.get('concepto','')} S/{e.get('monto',0):.2f} {e.get('fecha','')}", font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
        except Exception as e:
            ctk.CTkLabel(self.detalle_frame, text=f"Error: {e}").pack()

    def _detalle_neto_mes(self):
        from datetime import date
        hoy = date.today()
        ini = hoy.replace(day=1).isoformat()
        fin = hoy.isoformat()
        try:
            from controllers import egreso_controller
            rep = egreso_controller.reporte_ingresos_vs_egresos(ini, fin)
            txt = f"Ingresos: S/{rep.get('total_ingresos',0):.2f} (pagos {rep.get('ingresos_pagos',0):.2f} + ventas {rep.get('ingresos_ventas',0):.2f})\nEgresos: S/{rep.get('egresos',0):.2f}\nNeto: S/{rep.get('neto',0):.2f}"
            ctk.CTkLabel(self.detalle_frame, text=txt, font=ctk.CTkFont(size=14), justify="left").pack(anchor="w", pady=10)
        except Exception as e:
            ctk.CTkLabel(self.detalle_frame, text=f"Error: {e}").pack()

    def _detalle_nuevos_mes(self):
        ctk.CTkLabel(self.detalle_frame, text="Nuevos vs Antiguos: ver Reportes > Nuevos vs Antiguos", font=ctk.CTkFont(size=12)).pack(pady=20)

    def _detalle_antiguos_mes(self):
        self._detalle_nuevos_mes()

    def _detalle_matriculas_mes(self):
        ctk.CTkLabel(self.detalle_frame, text="Matrículas mes: ver listado detallado en Reportes", font=ctk.CTkFont(size=12)).pack(pady=20)

    def _detalle_stock(self):
        productos = dashboard_controller.listar_stock_bajo()

        ctk.CTkLabel(
            self.detalle_frame,
            text=f"Total: {len(productos)} productos con stock bajo",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(10, 5))

        if not productos:
            ctk.CTkLabel(self.detalle_frame, text="No hay productos con stock bajo").pack(pady=10)
            return

        header = ctk.CTkFrame(self.detalle_frame, fg_color="#DDD6E5")  # Morado claro
        header.pack(fill="x", padx=5, pady=2)

        for col, (texto, ancho) in enumerate([
            ("Código", 80), ("Nombre", 150), ("Categoría", 120),
            ("Stock Actual", 80), ("Stock Mínimo", 80)
        ]):
            ctk.CTkLabel(
                header, text=texto, width=ancho,
                font=ctk.CTkFont(size=12, weight="bold"),
            ).grid(row=0, column=col, padx=5, pady=5)

        for prod in productos:
            row = ctk.CTkFrame(self.detalle_frame)
            row.pack(fill="x", padx=5, pady=1)

            ctk.CTkLabel(row, text=str(prod.get("codigo", "")), width=80,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(prod.get("nombre", "")), width=150,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(prod.get("categoria_nombre", "")), width=120,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(prod.get("stock_actual", 0)), width=80,
                         font=ctk.CTkFont(size=11), text_color="red").grid(row=0, column=3, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(prod.get("stock_minimo", 0)), width=80,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=4, padx=5, pady=3)

    def _crear_grafico_barras_simple(self, etiquetas, valores, titulo):
        if not MATPLOTLIB_DISPONIBLE or not valores:
            return

        frame_grafico = ctk.CTkFrame(self.detalle_frame)
        frame_grafico.pack(fill="x", padx=5, pady=10)

        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)

        colores = ["#4CAF50" if v >= 0 else "#F44336" for v in valores]
        ax.bar(range(len(valores)), valores, color=colores, alpha=0.7)
        ax.set_xticks(range(len(etiquetas)))
        ax.set_xticklabels(etiquetas, rotation=45, ha="right", fontsize=8)
        ax.set_title(titulo, fontsize=12, fontweight="bold")
        ax.set_ylabel("Monto (S/)")
        ax.grid(axis="y", alpha=0.3)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
