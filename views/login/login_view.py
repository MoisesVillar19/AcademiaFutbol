import customtkinter as ctk
from pathlib import Path
from PIL import Image
from controllers import login_controller

COLOR_SIDEBAR  = "#3D1559"  # Morado oscuro
COLOR_PRIMARY  = "#7C3AED"  # Morado claro
COLOR_PRIMARY_H = "#6D28D9" # Morado claro hover
COLOR_BG       = "#F8F5FA"  # Blanco ligeramente morado
COLOR_TEXT_SEC = "#6B5B7B"  # Morado gris

ASSETS_DIR = Path(__file__).parent.parent.parent / "assets" / "images"


class LoginView(ctk.CTkToplevel):
    def __init__(self, parent, on_login_success=None):
        super().__init__(parent)
        self.title("Academia Deportiva - Inicio de Sesión")
        self.geometry("440x480")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        self.protocol("WM_DELETE_WINDOW", self._on_cerrar)
        self.on_login_success = on_login_success
        self._centrar_ventana()
        self._crear_widgets()
        self.after(50, self._elevar_ventana)

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = 440
        alto = 480
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _elevar_ventana(self):
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.after(200, lambda: self.attributes("-topmost", False))

    def _crear_widgets(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=40, pady=30)

        logo_path = ASSETS_DIR / "logo_roncalli.png"
        if logo_path.exists():
            logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(220, 70),
            )
            ctk.CTkLabel(
                frame, image=logo_image, text="",
            ).pack(pady=(0, 8))
        else:
            ctk.CTkLabel(
                frame, text="⚽",
                font=ctk.CTkFont(size=56),
            ).pack(pady=(0, 8))

        ctk.CTkLabel(
            frame, text="Academia Deportiva",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLOR_PRIMARY,
        ).pack(pady=(0, 3))

        ctk.CTkLabel(
            frame, text="Iniciar Sesión",
            font=ctk.CTkFont(size=13),
            text_color=COLOR_TEXT_SEC,
        ).pack(pady=(0, 30))

        self.entry_usuario = ctk.CTkEntry(
            frame, placeholder_text="👤  Usuario",
            width=320, height=44,
            border_width=1, border_color="#ced4da",
            corner_radius=10,
            font=ctk.CTkFont(size=13),
        )
        self.entry_usuario.pack(pady=7)

        self.entry_password = ctk.CTkEntry(
            frame, placeholder_text="🔒  Contraseña",
            width=320, height=44, show="•",
            border_width=1, border_color="#ced4da",
            corner_radius=10,
            font=ctk.CTkFont(size=13),
        )
        self.entry_password.pack(pady=7)

        self.btn_login = ctk.CTkButton(
            frame, text="Ingresar", width=320, height=46,
            corner_radius=10,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_H,
            command=self._on_login,
        )
        self.btn_login.pack(pady=(22, 10))

        self.label_error = ctk.CTkLabel(
            frame, text="", text_color="#dc3545",
            font=ctk.CTkFont(size=12),
        )
        self.label_error.pack()

        self.entry_password.bind("<Return>", lambda e: self._on_login())
        self.entry_usuario.focus()

    def _on_login(self):
        username = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()

        exito, mensaje, usuario = login_controller.iniciar_sesion(username, password)

        if exito:
            self.label_error.configure(text="")
            if self.on_login_success:
                self.on_login_success(usuario)
            self.destroy()
        else:
            self.label_error.configure(text=mensaje)

    def _on_cerrar(self):
        from database.connection import close_connection
        close_connection()
        self.master.destroy()
