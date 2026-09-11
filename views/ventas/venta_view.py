import customtkinter as ctk
from tkinter import filedialog, messagebox
import shutil, os
from controllers import venta_controller, login_controller
from controllers import inventario_controller
from utils.constants import COMPROBANTES_DIR


class VentaView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._productos_map = {}
        self._comprobante_tmp = None
        self._crear_widgets()
        self._cargar_productos()
        self._cargar_ventas()

    def _crear_widgets(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        self.tab_lista = self.tabview.add("Ventas")
        self.tab_form = self.tabview.add("Registrar Venta")
        self._crear_tab_lista()
        self._crear_tab_form()

    def _crear_tab_lista(self):
        from utils.ui_helpers import crear_seccion, crear_nota, crear_boton_interactivo
        sec = crear_seccion(
            self.tab_lista, titulo="Ventas", icono="🛒",
            descripcion="Uniformes / Tienda / Campeonato / Inscripción. Clic en ▾ Ver detalle para producto, cantidades y comprobante.",
            nro=1,
        )
        crear_boton_interactivo(sec, text="Actualizar", width=110, command=self._cargar_ventas,
                                fg_color="#7C3AED").pack(anchor="e", padx=10, pady=(0, 8))
        crear_nota(sec, "Tip: cada tarjeta se expande inline con el detalle completo.")
        self.scroll = ctk.CTkScrollableFrame(self.tab_lista)
        self.scroll.pack(fill="both", expand=True, padx=5, pady=5)
        self.label_lista_status = ctk.CTkLabel(self.tab_lista, text="", font=ctk.CTkFont(size=13, weight="bold"), text_color="#6B5B7B")
        self.label_lista_status.pack(pady=3)

    def _crear_tab_form(self):
        scroll = ctk.CTkScrollableFrame(self.tab_form)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(scroll, text="Registrar Venta", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0,10))
        ctk.CTkLabel(scroll, text="Producto *").pack(anchor="w")
        self.combo_producto = ctk.CTkComboBox(scroll, width=400, values=["Cargando..."])
        self.combo_producto.pack(anchor="w", pady=3)
        ctk.CTkLabel(scroll, text="Cantidad *").pack(anchor="w")
        self.entry_cant = ctk.CTkEntry(scroll, width=150, placeholder_text="1")
        self.entry_cant.pack(anchor="w", pady=3)
        self.entry_cant.insert(0, "1")
        ctk.CTkLabel(scroll, text="Tipo venta").pack(anchor="w")
        self.combo_tipo = ctk.CTkComboBox(scroll, width=200, values=["UNIFORME","TIENDA","CAMPEONATO","INSCRIPCION"], command=self._on_tipo_changed)
        self.combo_tipo.set("UNIFORME")
        self.combo_tipo.pack(anchor="w", pady=3)
        # CAMPEONATO por tarifa (división): sin producto obligatorio
        self.frame_campeonato = ctk.CTkFrame(scroll, fg_color="transparent")
        ctk.CTkLabel(self.frame_campeonato, text="Tarifa campeonato (división) *").pack(anchor="w")
        self.combo_tarifa_camp = ctk.CTkComboBox(self.frame_campeonato, width=400, values=["Cargando..."], command=self._on_tarifa_camp_changed)
        self.combo_tarifa_camp.pack(anchor="w", pady=3)
        ctk.CTkLabel(self.frame_campeonato, text="Monto a cobrar (S/) * — editable").pack(anchor="w")
        self.entry_monto_camp = ctk.CTkEntry(self.frame_campeonato, width=150, placeholder_text="0.00")
        self.entry_monto_camp.pack(anchor="w", pady=3)
        ctk.CTkLabel(self.frame_campeonato, text="↳ En CAMPEONATO el producto es opcional; el monto manda.", font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w")
        self._tarifas_camp_map = {}
        ctk.CTkLabel(scroll, text="Método pago").pack(anchor="w")
        self.combo_metodo = ctk.CTkComboBox(scroll, width=200, values=["EFECTIVO","YAPE","PLIN","TRANSFERENCIA"])
        self.combo_metodo.set("EFECTIVO")
        self.combo_metodo.pack(anchor="w", pady=3)
        ctk.CTkLabel(scroll, text="ID Estudiante (opcional, para reingreso/inscripción)").pack(anchor="w")
        self.entry_est = ctk.CTkEntry(scroll, width=200, placeholder_text="ID estudiante")
        self.entry_est.pack(anchor="w", pady=3)
        self.btn_comprobante = ctk.CTkButton(scroll, text="Subir comprobante (YAPE/PLIN)", width=200, command=self._elegir_comprobante)
        self.btn_comprobante.pack(anchor="w", pady=5)
        self.label_comp = ctk.CTkLabel(scroll, text="Sin comprobante", text_color="gray")
        self.label_comp.pack(anchor="w")
        self.label_status = ctk.CTkLabel(scroll, text="")
        self.label_status.pack(anchor="w", pady=5)
        ctk.CTkButton(scroll, text="Registrar Venta", width=150, command=self._registrar).pack(anchor="w", pady=10)

    def _cargar_productos(self):
        prods = inventario_controller.listar_productos(activo=1)
        nombres = [f"{p['codigo']} - {p['nombre']} (S/{p.get('precio_venta', p.get('precio',0)):.2f} stock:{p['stock_actual']})" for p in prods]
        self.combo_producto.configure(values=nombres if nombres else ["Sin productos"])
        self._productos_map = {n: p for n,p in zip(nombres, prods)}

    def _cargar_ventas(self):
        from utils.ui_helpers import crear_card_interactiva, agregar_detalle_expandible, linea_detalle, crear_lista_vacia
        for w in self.scroll.winfo_children():
            w.destroy()
        ventas = venta_controller.listar_ventas()
        if hasattr(self, "label_lista_status"):
            try:
                total = sum(v.get("monto_total", 0) for v in ventas)
                self.label_lista_status.configure(text=f"Total: {len(ventas)} venta(s) • S/{total:.2f}")
            except Exception:
                self.label_lista_status.configure(text=f"Total: {len(ventas)} venta(s)")
        if not ventas:
            crear_lista_vacia(self.scroll, "No hay ventas", "Registra la primera en la pestaña Registrar Venta")
            return
        for v in ventas:
            card = crear_card_interactiva(self.scroll)
            card.pack(fill="x", padx=6, pady=4)
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=10, pady=8)
            info = ctk.CTkFrame(top, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)
            try:
                titulo = f"{v['tipo_venta']} - {v['numero_recibo']} - S/{v['monto_total']:.2f} - {v['metodo_pago']}"
            except Exception:
                titulo = f"{v.get('tipo_venta','')} - {v.get('numero_recibo','')} - S/{v.get('monto_total',0)} - {v.get('metodo_pago','')}"
            ctk.CTkLabel(info, text=titulo, font=ctk.CTkFont(size=13, weight="bold"), text_color="#1F0A33").pack(anchor="w")
            ctk.CTkLabel(info, text=f"Fecha: {v.get('fecha_venta','')} | Comp: {v.get('comprobante_path','')}", text_color="#6B5B7B", font=ctk.CTkFont(size=12)).pack(anchor="w")
            badge = ctk.CTkFrame(top, fg_color="#F3E8FF", corner_radius=8)
            badge.pack(side="right", padx=10)
            try:
                ctk.CTkLabel(badge, text=f"S/{v.get('monto_total',0):.2f}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#7C3AED").pack(padx=10, pady=6)
            except Exception:
                pass

            def _poblar(frame, _v=v):
                linea_detalle(frame, "ID venta", _v.get("id_venta"))
                linea_detalle(frame, "Recibo", _v.get("numero_recibo"))
                linea_detalle(frame, "Tipo", _v.get("tipo_venta"))
                linea_detalle(frame, "Producto", _v.get("producto_nombre") or _v.get("nombre_producto"))
                linea_detalle(frame, "Cantidad", _v.get("cantidad"))
                linea_detalle(frame, "Precio unit.", _v.get("precio_unitario") or _v.get("precio"))
                linea_detalle(frame, "Método pago", _v.get("metodo_pago"))
                linea_detalle(frame, "Estudiante", _v.get("id_estudiante") or _v.get("estudiante"))
                linea_detalle(frame, "Comprobante", _v.get("comprobante_path"))
                linea_detalle(frame, "Fecha", _v.get("fecha_venta"))

            toggle_btn, _, _ = agregar_detalle_expandible(card, _poblar)
            toggle_btn.pack(anchor="e", padx=10, pady=(0, 8))

    def _elegir_comprobante(self):
        path = filedialog.askopenfilename(filetypes=[("Imagen","*.jpg *.jpeg *.png"),("Todos","*.*")])
        if path:
            os.makedirs(COMPROBANTES_DIR, exist_ok=True)
            self._comprobante_tmp = path
            self.label_comp.configure(text=os.path.basename(path))

    def _on_tipo_changed(self, selection):
        if selection == "CAMPEONATO":
            self.frame_campeonato.pack(anchor="w", pady=5, before=self.btn_comprobante)
            self._cargar_tarifas_campeonato()
        else:
            try:
                self.frame_campeonato.pack_forget()
            except Exception:
                pass

    def _cargar_tarifas_campeonato(self):
        try:
            from controllers import tarifa_controller
            tarifas = tarifa_controller.listar_tarifas_activas(tipo="CAMPEONATO")
        except Exception:
            tarifas = []
        nombres = [f"{t.get('categoria_nombre','')} - {t['nombre']} (S/{t['monto']:.2f})" for t in tarifas]
        self.combo_tarifa_camp.configure(values=nombres if nombres else ["Sin tarifas de campeonato"])
        self._tarifas_camp_map = {n: t for n, t in zip(nombres, tarifas)}

    def _on_tarifa_camp_changed(self, selection):
        t = self._tarifas_camp_map.get(selection)
        if t:
            self.entry_monto_camp.delete(0, "end")
            self.entry_monto_camp.insert(0, f"{t['monto']:.2f}")

    def _registrar(self):
        tipo = self.combo_tipo.get()
        comprobante_path = None
        if self._comprobante_tmp:
            os.makedirs(COMPROBANTES_DIR, exist_ok=True)
            comprobante_path = self._comprobante_tmp
        id_est = self.entry_est.get().strip()
        try:
            id_est = int(id_est) if id_est else None
        except ValueError:
            id_est = None
        if tipo == "CAMPEONATO":
            t = self._tarifas_camp_map.get(self.combo_tarifa_camp.get())
            if not t:
                self.label_status.configure(text="Seleccione tarifa de campeonato", text_color="red")
                return
            try:
                monto = float(self.entry_monto_camp.get().strip() or "0")
                if monto <= 0:
                    raise ValueError
            except ValueError:
                self.label_status.configure(text="Monto de campeonato inválido", text_color="red")
                return
            data = {
                "id_estudiante": id_est,
                "tipo_venta": tipo,
                "metodo_pago": self.combo_metodo.get(),
                "items": [],
                "id_tarifa": t["id_tarifa"],
                "monto_total": monto,
                "comprobante_path": comprobante_path,
            }
        else:
            sel = self.combo_producto.get()
            prod = self._productos_map.get(sel)
            if not prod:
                self.label_status.configure(text="Seleccione producto", text_color="red")
                return
            try:
                cant = int(self.entry_cant.get().strip() or "1")
                if cant <= 0:
                    raise ValueError
            except ValueError:
                self.label_status.configure(text="Cantidad inválida", text_color="red")
                return
            data = {
                "id_estudiante": id_est,
                "tipo_venta": tipo,
                "metodo_pago": self.combo_metodo.get(),
                "items": [{"id_producto": prod["id_producto"], "cantidad": cant}],
                "comprobante_path": comprobante_path,
            }
        exito, msg, vid = venta_controller.registrar_venta(data)
        if exito and comprobante_path and vid:
            # copiar a central con recibo
            try:
                import glob
                # el service ya generó recibo, obtener venta para nombre
                v = venta_controller.obtener_venta(vid)
                if v:
                    dest = os.path.join(COMPROBANTES_DIR, f"{v['numero_recibo']}.jpg")
                    shutil.copy2(comprobante_path, dest)
            except Exception:
                pass
            self._comprobante_tmp = None
            self.label_comp.configure(text="Sin comprobante")
        self.label_status.configure(text=msg, text_color="green" if exito else "red")
        if exito:
            self._cargar_productos()
            self._cargar_ventas()
