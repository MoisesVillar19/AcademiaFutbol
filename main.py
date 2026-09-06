import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

import customtkinter as ctk
from PIL import Image
from database.create_db import create_tables
from database.seed import seed_database
from database.connection import close_connection
from controllers import login_controller
from views.login.login_view import LoginView
from views.login.cambiar_password_view import CambiarPasswordView
from utils.constants import __version__
from updater import update_view

ASSETS_DIR = Path(__file__).parent / "assets" / "images"

# ── Colores globales (Instituto Roncalli) ────────────────────────
COLOR_SIDEBAR      = "#3D1559"  # Morado oscuro
COLOR_SIDEBAR_HOVER= "#4E1D70"  # Morado oscuro hover
COLOR_SIDEBAR_ACT  = "#6B21A8"  # Morado medio activo
COLOR_HEADER       = "#6B21A8"  # Morado medio
COLOR_PRIMARY      = "#7C3AED"  # Morado claro (botones principales)
COLOR_PRIMARY_HOVER= "#6D28D9"  # Morado claro hover
COLOR_BG           = "#F8F5FA"  # Blanco ligeramente morado
COLOR_CARD         = "#FFFFFF"  # Blanco puro
COLOR_TEXT         = "#1F0A33"  # Morado muy oscuro (texto principal)
COLOR_TEXT_SEC     = "#6B5B7B"  # Morado gris (texto secundario)
COLOR_SUCCESS      = "#22C55E"  # Verde (éxito)
COLOR_DANGER       = "#DC2626"  # Rojo (peligro)
COLOR_DANGER_HVR   = "#B91C1C"  # Rojo hover
COLOR_BORDER       = "#DDD6E5"  # Borde morado claro


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.title("Academia Deportiva")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(fg_color=COLOR_BG)
        self.protocol("WM_DELETE_WINDOW", self._on_cerrar)
        self._centrar_ventana()
        self._mostrar_bienvenida()

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = 1100
        alto = 700
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _mostrar_bienvenida(self):
        for widget in self.winfo_children():
            widget.destroy()

        frame = ctk.CTkFrame(self, fg_color=COLOR_BG)
        frame.pack(expand=True, fill="both")

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        logo_path = ASSETS_DIR / "logo_roncalli.png"
        if logo_path.exists():
            logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(280, 90),
            )
            ctk.CTkLabel(
                inner, image=logo_image, text="",
            ).pack(pady=(0, 15))
        else:
            ctk.CTkLabel(
                inner, text="⚽",
                font=ctk.CTkFont(size=72),
            ).pack(pady=(0, 10))

        ctk.CTkLabel(
            inner, text="Academia Deportiva",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLOR_PRIMARY,
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            inner, text=f"Sistema de Gestión v{__version__}",
            font=ctk.CTkFont(size=14),
            text_color=COLOR_TEXT_SEC,
        ).pack(pady=(0, 35))

        ctk.CTkButton(
            inner, text="Iniciar Sesión", width=260, height=50,
            corner_radius=12,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            command=self._abrir_login,
        ).pack()

    def _abrir_login(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.withdraw()
        LoginView(self, on_login_success=self._on_login_success)

    def _on_login_success(self, usuario):
        self.deiconify()
        self.lift()
        self.focus_force()
        if login_controller.necesita_cambiar_password():
            CambiarPasswordView(self, on_success=self._on_password_cambiado)
        else:
            self._mostrar_dashboard()

    def _on_password_cambiado(self):
        self._mostrar_dashboard()

    def _mostrar_dashboard(self):
        for widget in self.winfo_children():
            widget.destroy()

        # ── Sidebar ────────────────────────────────────────────────
        sidebar = ctk.CTkFrame(self, width=240, fg_color=COLOR_SIDEBAR)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        usuario = login_controller.obtener_usuario_actual()
        nombre = usuario.get("nombres", "") if usuario else ""
        rol = usuario.get("rol", "") if usuario else ""

        # Header del sidebar (fijo)
        header_frame = ctk.CTkFrame(sidebar, fg_color=COLOR_SIDEBAR)
        header_frame.pack(fill="x", padx=15, pady=(20, 5))

        logo_path = ASSETS_DIR / "logo_roncalli.png"
        if logo_path.exists():
            logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(190, 64),
            )
            ctk.CTkLabel(header_frame, image=logo_image, text="").pack(anchor="w")
        else:
            ctk.CTkLabel(header_frame, text="⚽ Academia", font=ctk.CTkFont(size=26, weight="bold"), text_color="#ffffff").pack(anchor="w")

        ctk.CTkLabel(header_frame, text="Academia Deportiva", font=ctk.CTkFont(size=19, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(header_frame, text="Gestión integral", font=ctk.CTkFont(size=11), text_color="#c0c8d4").pack(anchor="w")

        # Info del usuario (más grande)
        user_frame = ctk.CTkFrame(sidebar, fg_color=COLOR_SIDEBAR_HOVER, corner_radius=10)
        user_frame.pack(fill="x", padx=12, pady=(10, 12))
        ctk.CTkLabel(user_frame, text=f"👤  {nombre}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#ffffff", anchor="w").pack(fill="x", padx=10, pady=(8, 0))
        ctk.CTkLabel(user_frame, text=f"   {rol} • En línea", font=ctk.CTkFont(size=11), text_color="#8899aa", anchor="w").pack(fill="x", padx=10, pady=(0, 8))

        ctk.CTkFrame(sidebar, fg_color=COLOR_SIDEBAR_HOVER, height=1).pack(fill="x", padx=15, pady=6)

        # ── Menú agrupado SCROLLEABLE (5 grupos) ─────────────────
        menu_scroll = ctk.CTkScrollableFrame(sidebar, fg_color="transparent", scrollbar_button_color=COLOR_SIDEBAR_HOVER, scrollbar_button_hover_color=COLOR_SIDEBAR_ACT)
        menu_scroll.pack(fill="both", expand=True, padx=2, pady=2)

        self._boton_activo = None
        self._sidebar_botones = []

        def _header(text):
            lbl = ctk.CTkLabel(menu_scroll, text=text, font=ctk.CTkFont(size=11, weight="bold"), text_color="#9CA3AF", anchor="w")
            lbl.pack(fill="x", padx=12, pady=(10, 3))

        def _btn(text, cmd, indent=False):
            w = 200 if not indent else 186
            pad = 8 if not indent else 20
            btn = ctk.CTkButton(
                menu_scroll, text=text, width=w, height=38,
                fg_color="transparent", anchor="w",
                font=ctk.CTkFont(size=14 if not indent else 13, weight="bold" if not indent else "normal"),
                text_color="#E5E7EB" if not indent else "#cbd5e1",
                hover_color="#4E1D70" if not indent else "#3A1A5E",
                corner_radius=8,
                command=lambda c=cmd, b=text: self._on_menu_click(c, b),
            )
            btn.pack(pady=2, padx=pad)
            self._sidebar_botones.append((text, btn))
            try:
                btn.bind("<Enter>", lambda e, b=btn: (b.configure(cursor="hand2"), b.configure(border_width=1, border_color="#7C3AED") if indent else None))
                btn.bind("<Leave>", lambda e, b=btn: (b.configure(cursor=""), b.configure(border_width=0) if indent else None))
            except Exception:
                pass
            return btn

        _header("PANEL")
        _btn("📊  Dashboard", self._mostrar_placeholder)
        _header("ACADEMIA")
        _btn("👤  Estudiantes", self._mostrar_estudiantes, indent=True)
        _btn("📋  Matrículas", self._mostrar_matriculas, indent=True)
        _header("FINANZAS")
        _btn("💰  Pagos", self._mostrar_pagos, indent=True)
        _btn("🛒  Ventas", self._mostrar_ventas, indent=True)
        if login_controller.es_admin():
            _btn("💸  Egresos", self._mostrar_egresos, indent=True)
        _header("ALMACÉN")
        _btn("📦  Inventario", self._mostrar_inventario, indent=True)
        _header("ANÁLISIS")
        _btn("📈  Reportes", self._mostrar_reportes, indent=True)

        if login_controller.es_admin():
            _header("SISTEMA")
            _btn("📤  Importar", self._mostrar_importar, indent=True)
            _btn("🔑  Usuarios", self._mostrar_usuarios, indent=True)
            _btn("🏷️  Tarifas", self._mostrar_tarifas, indent=True)
            _btn("📝  Auditoría", self._mostrar_auditoria, indent=True)
            _btn("⚙️  Configuración", self._mostrar_configuracion, indent=True)
            _btn("💾  Respaldo", self._crear_backup_manual, indent=True)

        # Espaciador para scroll completo
        ctk.CTkLabel(menu_scroll, text="", height=10).pack()

        # Botón cerrar sesión
        ctk.CTkFrame(sidebar, fg_color=COLOR_SIDEBAR_HOVER, height=1).pack(
            fill="x", padx=15, side="bottom", pady=(5, 0)
        )
        ctk.CTkButton(
            sidebar, text="🚪  Cerrar Sesión", width=196, height=38,
            fg_color=COLOR_DANGER, hover_color=COLOR_DANGER_HVR,
            font=ctk.CTkFont(size=13),
            corner_radius=8,
            command=self._cerrar_sesion,
        ).pack(side="bottom", pady=15, padx=12)

        # ── Contenido principal ────────────────────────────────────
        self.contenido = ctk.CTkFrame(self, fg_color=COLOR_BG)
        self.contenido.pack(side="right", fill="both", expand=True)

        self._mostrar_placeholder()
        self.after(5000, self._verificar_backup_automatico)

    def _crear_backup_manual(self):
        from tkinter import messagebox
        from controllers import configuracion_controller
        exito, msg, ruta = configuracion_controller.crear_backup_manual()
        if exito:
            messagebox.showinfo("Respaldo", f"{msg}\n\n{ruta}")
        else:
            messagebox.showerror("Respaldo", msg)

    def _verificar_backup_automatico(self):
        """RN-030: respaldo automatico segun CONFIGURACION; revisa cada 6 horas."""
        try:
            from controllers import configuracion_controller
            exito, msg = configuracion_controller.verificar_backup_automatico()
            if exito:
                from tkinter import messagebox
                messagebox.showinfo("Respaldo automático", msg)
        except Exception as e:
            from utils.logger import logger
            logger.error(f"Error en backup automático: {e}")
        try:
            self.after(6 * 3600 * 1000, self._verificar_backup_automatico)
        except Exception:
            pass

    def _on_menu_click(self, command, label):
        for text, btn in self._sidebar_botones:
            if text == label:
                btn.configure(fg_color=COLOR_SIDEBAR_ACT, text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color="#c0c8d4")
        command()

    def _limpiar_contenido(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()

    def _mostrar_placeholder(self):
        self._limpiar_contenido()
        from views.dashboard.dashboard_view import DashboardView
        DashboardView(self.contenido).pack(fill="both", expand=True)

    def _mostrar_usuarios(self):
        self._limpiar_contenido()
        from views.usuarios.usuario_view import UsuarioView
        UsuarioView(self.contenido).pack(fill="both", expand=True)

    def _mostrar_estudiantes(self):
        self._limpiar_contenido()
        from views.estudiantes.estudiante_view import EstudianteView
        EstudianteView(self.contenido).pack(fill="both", expand=True)

    def _mostrar_matriculas(self):
        self._limpiar_contenido()
        from views.matriculas.matricula_view import MatriculaView
        MatriculaView(self.contenido).pack(fill="both", expand=True)

    def _mostrar_pagos(self):
        self._limpiar_contenido()
        from views.pagos.pago_view import PagoView
        PagoView(self.contenido).pack(fill="both", expand=True)

    def _mostrar_inventario(self):
        self._limpiar_contenido()
        from views.inventario.inventario_view import InventarioView
        InventarioView(self.contenido).pack(fill="both", expand=True)

    def _mostrar_importar(self):
        self._limpiar_contenido()
        from views.importar.importar_view import ImportarView
        ImportarView(self.contenido).pack(fill="both", expand=True)

    def _mostrar_reportes(self):
        self._limpiar_contenido()
        from views.reportes.reporte_view import ReporteView
        ReporteView(self.contenido).pack(fill="both", expand=True)

    def _mostrar_auditoria(self):
        self._limpiar_contenido()
        from views.auditoria.auditoria_view import AuditoriaView
        AuditoriaView(self.contenido).pack(fill="both", expand=True)

    def _mostrar_tarifas(self):
        self._limpiar_contenido()
        from views.tarifas.tarifa_view import TarifaView
        TarifaView(self.contenido).pack(fill="both", expand=True)

    def _mostrar_ventas(self):
        self._limpiar_contenido()
        from views.ventas.venta_view import VentaView
        VentaView(self.contenido).pack(fill="both", expand=True)

    def _mostrar_egresos(self):
        self._limpiar_contenido()
        from views.egresos.egreso_view import EgresoView
        EgresoView(self.contenido).pack(fill="both", expand=True)

    def _mostrar_configuracion(self):
        self._limpiar_contenido()
        from views.configuracion.configuracion_view import ConfiguracionView
        ConfiguracionView(self.contenido).pack(fill="both", expand=True)

    def _cerrar_sesion(self):
        login_controller.cerrar_sesion()
        self._mostrar_bienvenida()

    def _on_cerrar(self):
        login_controller.cerrar_sesion()
        close_connection()
        self.destroy()


def initialize_system() -> None:
    create_tables()
    seed_database()


def main() -> None:
    try:
        initialize_system()
        app = App()
        app.after(2000, lambda: update_view.verificar_y_mostrar(app))
        app.mainloop()
    except Exception as e:
        print(f"Error al inicializar el sistema: {e}")
    finally:
        close_connection()


if __name__ == "__main__":
    main()
