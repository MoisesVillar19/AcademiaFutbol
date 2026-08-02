import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import customtkinter as ctk
from database.create_db import create_tables
from database.seed import seed_database
from database.connection import close_connection
from controllers import login_controller
from views.login.login_view import LoginView
from views.login.cambiar_password_view import CambiarPasswordView


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Academia Deportiva")
        self.geometry("1024x680")
        self.minsize(800, 600)
        self.protocol("WM_DELETE_WINDOW", self._on_cerrar)
        self._centrar_ventana()
        self._mostrar_bienvenida()

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = 1024
        alto = 680
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _mostrar_bienvenida(self):
        for widget in self.winfo_children():
            widget.destroy()

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True)

        ctk.CTkLabel(
            frame, text="⚽",
            font=ctk.CTkFont(size=64),
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            frame, text="Academia Deportiva",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#1f6aa5",
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            frame, text="Sistema de Gestión",
            font=ctk.CTkFont(size=16),
            text_color="gray",
        ).pack(pady=(0, 30))

        ctk.CTkButton(
            frame, text="Iniciar Sesión", width=220, height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._abrir_login,
        ).pack()

    def _abrir_login(self):
        for widget in self.winfo_children():
            widget.destroy()
        LoginView(self, on_login_success=self._on_login_success)

    def _on_login_success(self, usuario):
        if login_controller.necesita_cambiar_password():
            CambiarPasswordView(self, on_success=self._on_password_cambiado)
        else:
            self._mostrar_dashboard()

    def _on_password_cambiado(self):
        self._mostrar_dashboard()

    def _mostrar_dashboard(self):
        for widget in self.winfo_children():
            widget.destroy()

        sidebar = ctk.CTkFrame(self, width=200, fg_color=("gray85", "gray20"))
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        usuario = login_controller.obtener_usuario_actual()
        nombre = usuario.get("nombres", "") if usuario else ""
        rol = usuario.get("rol", "") if usuario else ""

        ctk.CTkLabel(
            sidebar, text="⚽ Academia",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            sidebar, text=f"{nombre}\n({rol})",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(pady=(0, 15))

        self.contenido = ctk.CTkFrame(self, fg_color="transparent")
        self.contenido.pack(side="right", fill="both", expand=True)

        botones = [
            ("📊 Dashboard", self._mostrar_placeholder),
            ("👤 Estudiantes", self._mostrar_estudiantes),
            ("📋 Matrículas", self._mostrar_matriculas),
            ("💰 Pagos", self._mostrar_pagos),
            ("📦 Inventario", self._mostrar_inventario),
            ("📈 Reportes", self._mostrar_reportes),
        ]

        if login_controller.es_admin():
            botones.append(("🔑 Usuarios", self._mostrar_usuarios))
            botones.append(("🏷️ Tarifas", self._mostrar_tarifas))
            botones.append(("📝 Auditoría", self._mostrar_auditoria))
            botones.append(("⚙️ Configuración", self._mostrar_configuracion))

        for text, command in botones:
            ctk.CTkButton(
                sidebar, text=text, width=180, height=36,
                fg_color="transparent", anchor="w",
                command=command,
            ).pack(pady=2, padx=10)

        ctk.CTkButton(
            sidebar, text="🚪 Cerrar Sesión", width=180, height=36,
            fg_color="red", hover_color="darkred",
            command=self._cerrar_sesion,
        ).pack(side="bottom", pady=15)

        self._mostrar_placeholder()

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
        app.mainloop()
    except Exception as e:
        print(f"Error al inicializar el sistema: {e}")
    finally:
        close_connection()


if __name__ == "__main__":
    main()
