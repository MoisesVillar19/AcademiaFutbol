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


def _num(v, default=0.0):
    """Número seguro para formateo: None/texto inválido → default (BD real trae NULLs)."""
    try:
        if v is None or v == "":
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._crear_widgets()
        self._cargar_indicadores()

    def _crear_widgets(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=15, pady=(15, 5))

        self.titulo_label = ctk.CTkLabel(
            self.header, text="📊  Dashboard  •  Resumen operativo",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#3D1559",
        )
        self.titulo_label.pack(side="left")
        ctk.CTkLabel(self.header, text="  Clic en una tarjeta para detalle  •  Datos en tiempo real", font=ctk.CTkFont(size=12), text_color="#9CA3AF").pack(side="left", padx=12)

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

        self._crear_card(row2, "Pagos Hoy", str(data.get("pagos_hoy", 0) or 0), "#22C55E",
                         lambda: self._mostrar_detalle("pagos_hoy"))
        self._crear_card(row2, "Ingresos Hoy", f"S/{_num(data.get('ingresos_hoy')):.2f}", "#22C55E",
                         lambda: self._mostrar_detalle("ingresos_hoy"))
        self._crear_card(row2, "Ingresos Mes", f"S/{_num(data.get('ingresos_mes')):.2f}", "#6B21A8",
                         lambda: self._mostrar_detalle("ingresos_mes"))

        row3 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)

        self._crear_card(row3, "Monto Vencido", f"S/{_num(data.get('monto_vencido')):.2f}", "#DC2626",
                         lambda: self._mostrar_detalle("monto_vencido"))
        self._crear_card(row3, "Monto por Vencer", f"S/{_num(data.get('monto_por_vencer')):.2f}", "#F59E0B",
                         lambda: self._mostrar_detalle("monto_por_vencer"))
        self._crear_card(row3, "Stock Bajo", str(data["stock_bajo"]), "#F59E0B",
                         lambda: self._mostrar_detalle("stock"))

        # Helper para mostrar — si es None (error) muestra —
        def _fmt(v, suf=""):
            if v is None:
                return "—"
            try:
                return f"S/{v:.2f}{suf}" if isinstance(v, (int, float)) else str(v)
            except Exception:
                return str(v)

        # 3 cards por fila: con 4 la última se corta (overflow horizontal)
        row4 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)

        self._crear_card(row4, "Ventas Mes", _fmt(data.get('ingresos_ventas_mes')), "#7C3AED",
                         lambda: self._mostrar_detalle("ventas_mes"))
        self._crear_card(row4, "Egresos Mes", _fmt(data.get('egresos_mes')), "#DC2626",
                         lambda: self._mostrar_detalle("egresos_mes"))
        neto = data.get('neto_mes')
        self._crear_card(row4, "Neto Mes", _fmt(neto), "#22C55E" if (neto or 0) >=0 else "#DC2626",
                         lambda: self._mostrar_detalle("neto_mes"))

        row5 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row5.pack(fill="x", pady=5)

        # MoM si existe (en fila propia para no cortar)
        mom = data.get('mom_ingresos')
        if mom is not None:
            mom_txt = f"{mom:+.1f}% vs mes anterior"
            mom_color = "#22C55E" if mom >=0 else "#DC2626"
            self._crear_card(row5, "MoM Ingresos", mom_txt, mom_color, lambda: self._mostrar_detalle("ingresos_mes"))
        self._crear_card(row5, "Nuevos Mes", str(data.get("nuevos_mes",0)), "#22C55E",
                         lambda: self._mostrar_detalle("nuevos_mes"))
        self._crear_card(row5, "Antiguos Mes", str(data.get("antiguos_mes",0)), "#6B21A8",
                         lambda: self._mostrar_detalle("antiguos_mes"))

        row6 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row6.pack(fill="x", pady=5)

        self._crear_card(row6, "Total Matrículas Mes", str(data.get("matriculas_mes",0)), "#3D1559",
                         lambda: self._mostrar_detalle("matriculas_mes"))

        for widget in self.detalle_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.detalle_frame,
            text="Haga clic en cualquier card para ver el detalle",
            font=ctk.CTkFont(size=14), text_color="gray",
        ).pack(expand=True)

    def _crear_card(self, parent, titulo, valor, color, comando):
        # Card clickeable estilo Configuración (frame blanco, sin hover que
        # repinte). NOTA: antes era CTkButton, pero en CustomTkinter 6 el
        # botón es un compuesto (frame+canvas+label internos) que se traga
        # los clics: solo el borde respondía. Con frame + clic propagado a
        # TODO el interior, cualquier punto abre el detalle (sin doble
        # disparo: los frames/labels no tienen comando nativo).
        card = ctk.CTkFrame(
            parent, fg_color="white",
            border_width=1, border_color="#E5E7EB",
            corner_radius=12,
        )
        card.pack(side="left", padx=6, pady=6, fill="x", expand=True)

        frame_interno = ctk.CTkFrame(card, fg_color="transparent")
        frame_interno.pack(expand=True, fill="both", padx=8, pady=8)

        ctk.CTkLabel(frame_interno, text=titulo, font=ctk.CTkFont(size=13, weight="bold"), text_color="#6B5B7B").pack(pady=(6, 2))
        ctk.CTkLabel(frame_interno, text=valor, font=ctk.CTkFont(size=26, weight="bold"), text_color=color).pack(pady=(2, 6))
        # sutil línea color
        ctk.CTkFrame(frame_interno, fg_color=color, height=3, corner_radius=2).pack(fill="x", padx=20, pady=(0,4))

        try:
            def _hacer_clickeable(w):
                try:
                    w.bind("<Button-1>", lambda e: comando(), add="+")
                except Exception:
                    pass
                try:
                    w.configure(cursor="hand2")
                except Exception:
                    pass
                try:
                    hijos = w.winfo_children()
                except Exception:
                    return
                for ch in hijos:
                    _hacer_clickeable(ch)
            _hacer_clickeable(card)
        except Exception:
            pass

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

        try:
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
        except Exception as e:
            from utils.logger import logger
            logger.error(f"Dashboard detalle '{tipo}' fallo: {e}", exc_info=True)
            ctk.CTkLabel(
                self.detalle_frame,
                text=f"⚠ No se pudo cargar el detalle: {e}",
                font=ctk.CTkFont(size=13), text_color="red",
                wraplength=600, justify="left",
            ).pack(pady=20)
        try:
            self.detalle_frame.update_idletasks()
        except Exception:
            pass

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
            ctk.CTkLabel(row, text=f"S/{_num(cuota.get('saldo')):.2f}", width=80,
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
            ctk.CTkLabel(row, text=f"S/{_num(pago.get('monto_total')):.2f}", width=80,
                         font=ctk.CTkFont(size=11), text_color="green").grid(row=0, column=1, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(pago.get("metodo_pago", "")), width=100,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(pago.get("fecha_pago", "")), width=100,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=5, pady=3)

    def _detalle_ingresos_hoy(self):
        pagos = dashboard_controller.listar_pagos_hoy()
        total = sum(_num(p.get("monto_total")) for p in pagos)

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
                [_num(p.get("monto_total")) for p in pagos],
                "Ingresos por Transacción",
            )

        # tabla siempre (aunque haya gráfico): recibo / monto / método
        header = ctk.CTkFrame(self.detalle_frame, fg_color="#DDD6E5")
        header.pack(fill="x", padx=5, pady=2)
        for col, (texto, ancho) in enumerate([
            ("N° Recibo", 120), ("Monto", 100), ("Método", 120)
        ]):
            ctk.CTkLabel(header, text=texto, width=ancho,
                         font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=col, padx=5, pady=5)
        for pago in pagos[:30]:
            row = ctk.CTkFrame(self.detalle_frame)
            row.pack(fill="x", padx=5, pady=1)
            ctk.CTkLabel(row, text=str(pago.get("numero_recibo", "")), width=120,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=5, pady=3)
            ctk.CTkLabel(row, text=f"S/{_num(pago.get('monto_total')):.2f}", width=100,
                         font=ctk.CTkFont(size=11), text_color="green").grid(row=0, column=1, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(pago.get("metodo_pago", "")), width=120,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=5, pady=3)
        if len(pagos) > 30:
            ctk.CTkLabel(self.detalle_frame, text=f"Mostrando 30 de {len(pagos)} pagos",
                         text_color="gray").pack(pady=5)

    def _detalle_ingresos_mes(self):
        datos = dashboard_controller.obtener_ingresos_por_dia_mes()
        total = sum(_num(d.get("monto")) for d in datos)

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
                [_num(d.get("monto")) for d in datos],
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
            ctk.CTkLabel(row, text=f"S/{_num(d.get('monto')):.2f}", width=100,
                         font=ctk.CTkFont(size=11), text_color="green").grid(row=0, column=1, padx=5, pady=3)

    def _detalle_monto(self, cuotas, tipo):
        total = sum(_num(c.get("saldo")) for c in cuotas)

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
            saldos = [_num(c.get("saldo")) for c in cuotas[:10]]
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
            ctk.CTkLabel(row, text=f"S/{_num(c.get('saldo')):.2f}", width=100,
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
            total = sum(_num(v.get("monto_total")) for v in ventas)
            ctk.CTkLabel(self.detalle_frame, text=f"Ventas mes: S/{total:.2f} en {len(ventas)} ventas", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10,5))
            for v in ventas[:20]:
                row = ctk.CTkFrame(self.detalle_frame)
                row.pack(fill="x", padx=5, pady=1)
                ctk.CTkLabel(row, text=f"{v.get('tipo_venta','')} {v.get('numero_recibo','')} S/{_num(v.get('monto_total')):.2f}", font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
        except Exception as e:
            ctk.CTkLabel(self.detalle_frame, text=f"Error: {e}").pack()

    def _detalle_egresos_mes(self):
        from datetime import date
        hoy = date.today()
        ini = hoy.replace(day=1).isoformat()
        try:
            from controllers import egreso_controller
            egresos = egreso_controller.listar_egresos(ini, hoy.isoformat())
            total = sum(_num(e.get("monto")) for e in egresos)
            ctk.CTkLabel(self.detalle_frame, text=f"Egresos mes: S/{total:.2f} en {len(egresos)}", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10,5))
            for e in egresos[:20]:
                row = ctk.CTkFrame(self.detalle_frame)
                row.pack(fill="x", padx=5, pady=1)
                ctk.CTkLabel(row, text=f"{e.get('concepto','')} S/{_num(e.get('monto')):.2f} {e.get('fecha','')}", font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
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
            txt = f"Ingresos: S/{_num(rep.get('total_ingresos')):.2f} (pagos {_num(rep.get('ingresos_pagos')):.2f} + ventas {_num(rep.get('ingresos_ventas')):.2f})\nEgresos: S/{_num(rep.get('egresos')):.2f}\nNeto: S/{_num(rep.get('neto')):.2f}"
            ctk.CTkLabel(self.detalle_frame, text=txt, font=ctk.CTkFont(size=14), justify="left").pack(anchor="w", pady=10)
        except Exception as e:
            ctk.CTkLabel(self.detalle_frame, text=f"Error: {e}").pack()

    def _detalle_nuevos_mes(self):
        alumnos = dashboard_controller.listar_nuevos_mes()

        ctk.CTkLabel(
            self.detalle_frame,
            text=f"Total: {len(alumnos)} alumnos nuevos este mes",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(10, 5))

        if not alumnos:
            ctk.CTkLabel(self.detalle_frame, text="No hay alumnos nuevos este mes").pack(pady=10)
            return

        header = ctk.CTkFrame(self.detalle_frame, fg_color="#DDD6E5")
        header.pack(fill="x", padx=5, pady=2)

        for col, (texto, ancho) in enumerate([
            ("DNI", 80), ("Nombre", 220), ("Ingreso", 100), ("Teléfono", 110)
        ]):
            ctk.CTkLabel(
                header, text=texto, width=ancho,
                font=ctk.CTkFont(size=12, weight="bold"),
            ).grid(row=0, column=col, padx=5, pady=5)

        for alumno in alumnos[:50]:
            row = ctk.CTkFrame(self.detalle_frame)
            row.pack(fill="x", padx=5, pady=1)

            ctk.CTkLabel(row, text=str(alumno.get("dni", "")), width=80,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=5, pady=3)
            ctk.CTkLabel(row, text=f"{alumno.get('nombres', '')} {alumno.get('apellidos', '')}",
                         width=220, font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(alumno.get("fecha_ingreso", "")), width=100,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(alumno.get("telefono", "")), width=110,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=5, pady=3)

        if len(alumnos) > 50:
            ctk.CTkLabel(
                self.detalle_frame,
                text=f"Mostrando 50 de {len(alumnos)} alumnos",
                text_color="gray",
            ).pack(pady=5)

    def _detalle_antiguos_mes(self):
        matriculas = dashboard_controller.listar_antiguos_mes()

        ctk.CTkLabel(
            self.detalle_frame,
            text=f"Total: {len(matriculas)} matrículas de antiguos este mes",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(10, 5))

        if not matriculas:
            ctk.CTkLabel(self.detalle_frame, text="No hay matrículas de antiguos este mes").pack(pady=10)
            return

        self._tabla_matriculas_mes(matriculas)

    def _detalle_matriculas_mes(self):
        matriculas = dashboard_controller.listar_matriculas_mes()

        ctk.CTkLabel(
            self.detalle_frame,
            text=f"Total: {len(matriculas)} matrículas este mes",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(10, 5))

        if not matriculas:
            ctk.CTkLabel(self.detalle_frame, text="No hay matrículas este mes").pack(pady=10)
            return

        self._tabla_matriculas_mes(matriculas)

    def _tabla_matriculas_mes(self, matriculas):
        header = ctk.CTkFrame(self.detalle_frame, fg_color="#DDD6E5")
        header.pack(fill="x", padx=5, pady=2)

        for col, (texto, ancho) in enumerate([
            ("Estudiante", 200), ("DNI", 80), ("Tarifa", 150), ("Inicio", 100)
        ]):
            ctk.CTkLabel(
                header, text=texto, width=ancho,
                font=ctk.CTkFont(size=12, weight="bold"),
            ).grid(row=0, column=col, padx=5, pady=5)

        for mat in matriculas[:50]:
            row = ctk.CTkFrame(self.detalle_frame)
            row.pack(fill="x", padx=5, pady=1)

            nombre = f"{mat.get('nombres', '')} {mat.get('apellidos', '')}"
            ctk.CTkLabel(row, text=nombre, width=200,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(mat.get("dni", "")), width=80,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(mat.get("tarifa_nombre", "")), width=150,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=5, pady=3)
            ctk.CTkLabel(row, text=str(mat.get("fecha_inicio", "")), width=100,
                         font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=5, pady=3)

        if len(matriculas) > 50:
            ctk.CTkLabel(
                self.detalle_frame,
                text=f"Mostrando 50 de {len(matriculas)} matrículas",
                text_color="gray",
            ).pack(pady=5)

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
