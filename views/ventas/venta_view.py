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
        header = ctk.CTkFrame(self.tab_lista, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(header, text="Ventas (Uniformes / Tienda / Campeonato / Inscripción)", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="Actualizar", width=100, command=self._cargar_ventas).pack(side="right")
        self.scroll = ctk.CTkScrollableFrame(self.tab_lista)
        self.scroll.pack(fill="both", expand=True, padx=5, pady=5)

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
        self.combo_tipo = ctk.CTkComboBox(scroll, width=200, values=["UNIFORME","TIENDA","CAMPEONATO","INSCRIPCION"])
        self.combo_tipo.set("UNIFORME")
        self.combo_tipo.pack(anchor="w", pady=3)
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
        for w in self.scroll.winfo_children():
            w.destroy()
        ventas = venta_controller.listar_ventas()
        if not ventas:
            ctk.CTkLabel(self.scroll, text="No hay ventas", text_color="gray").pack(pady=20)
            return
        for v in ventas:
            card = ctk.CTkFrame(self.scroll)
            card.pack(fill="x", padx=5, pady=3)
            ctk.CTkLabel(card, text=f"{v['tipo_venta']} - {v['numero_recibo']} - S/{v['monto_total']:.2f} - {v['metodo_pago']}", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=10, pady=5)
            ctk.CTkLabel(card, text=f"Fecha: {v['fecha_venta']} | Comp: {v.get('comprobante_path','')}", text_color="gray").pack(anchor="w", padx=10)

    def _elegir_comprobante(self):
        path = filedialog.askopenfilename(filetypes=[("Imagen","*.jpg *.jpeg *.png"),("Todos","*.*")])
        if path:
            os.makedirs(COMPROBANTES_DIR, exist_ok=True)
            self._comprobante_tmp = path
            self.label_comp.configure(text=os.path.basename(path))

    def _registrar(self):
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
        comprobante_path = None
        if self._comprobante_tmp:
            os.makedirs(COMPROBANTES_DIR, exist_ok=True)
            # se copiará tras generar recibo; por ahora guardamos tmp y lo copia service? aquí lo copiamos con nombre temporal
            comprobante_path = self._comprobante_tmp
        id_est = self.entry_est.get().strip()
        try:
            id_est = int(id_est) if id_est else None
        except ValueError:
            id_est = None
        data = {
            "id_estudiante": id_est,
            "tipo_venta": self.combo_tipo.get(),
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
