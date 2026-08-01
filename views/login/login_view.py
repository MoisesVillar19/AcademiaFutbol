import customtkinter as ctk
from controllers import login_controller


class LoginView(ctk.CTkToplevel):
    def __init__(self, parent, on_login_success=None):
        super().__init__(parent)
        self.title("Academia Deportiva - Inicio de Sesión")
        self.geometry("400x350")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_cerrar)
        self.on_login_success = on_login_success
        self._crear_widgets()

    def _crear_widgets(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=40, pady=30)

        ctk.CTkLabel(
            frame, text="Iniciar Sesión",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(pady=(0, 20))

        self.entry_usuario = ctk.CTkEntry(
            frame, placeholder_text="Usuario", width=280, height=40,
        )
        self.entry_usuario.pack(pady=5)

        self.entry_password = ctk.CTkEntry(
            frame, placeholder_text="Contraseña", width=280, height=40, show="*",
        )
        self.entry_password.pack(pady=5)

        self.btn_login = ctk.CTkButton(
            frame, text="Ingresar", width=280, height=40,
            command=self._on_login,
        )
        self.btn_login.pack(pady=20)

        self.label_error = ctk.CTkLabel(
            frame, text="", text_color="red", font=ctk.CTkFont(size=12),
        )
        self.label_error.pack()

        self.entry_password.bind("<Return>", lambda e: self._on_login())

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
