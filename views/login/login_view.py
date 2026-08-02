import customtkinter as ctk
from controllers import login_controller


class LoginView(ctk.CTkToplevel):
    def __init__(self, parent, on_login_success=None):
        super().__init__(parent)
        self.title("Academia Deportiva - Inicio de Sesión")
        self.geometry("420x400")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_cerrar)
        self.on_login_success = on_login_success
        self._centrar_ventana()
        self._crear_widgets()
        self.after(50, self._elevar_ventana)

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = 420
        alto = 400
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

        ctk.CTkLabel(
            frame, text="⚽",
            font=ctk.CTkFont(size=48),
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            frame, text="Academia Deportiva",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1f6aa5",
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            frame, text="Iniciar Sesión",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        ).pack(pady=(0, 25))

        self.entry_usuario = ctk.CTkEntry(
            frame, placeholder_text="👤  Usuario",
            width=300, height=42,
            border_width=1,
            corner_radius=8,
        )
        self.entry_usuario.pack(pady=6)

        self.entry_password = ctk.CTkEntry(
            frame, placeholder_text="🔒  Contraseña",
            width=300, height=42, show="•",
            border_width=1,
            corner_radius=8,
        )
        self.entry_password.pack(pady=6)

        self.btn_login = ctk.CTkButton(
            frame, text="Ingresar", width=300, height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_login,
        )
        self.btn_login.pack(pady=(20, 10))

        self.label_error = ctk.CTkLabel(
            frame, text="", text_color="#e74c3c",
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
