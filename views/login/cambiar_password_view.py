import customtkinter as ctk
from controllers import login_controller


class CambiarPasswordView(ctk.CTkToplevel):
    def __init__(self, parent, on_success=None):
        super().__init__(parent)
        self.title("Cambiar Contraseña - Primer Acceso")
        self.geometry("420x420")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_cerrar)
        self.on_success = on_success
        self._crear_widgets()

    def _crear_widgets(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=40, pady=30)

        ctk.CTkLabel(
            frame, text="Cambiar Contraseña",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            frame, text="Es su primer acceso. Debe cambiar la contraseña.",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(pady=(0, 20))

        self.entry_password_actual = ctk.CTkEntry(
            frame, placeholder_text="Contraseña actual", width=300, height=38, show="*",
        )
        self.entry_password_actual.pack(pady=5)

        self.entry_password_nuevo = ctk.CTkEntry(
            frame, placeholder_text="Nueva contraseña (mín. 6 caracteres)", width=300, height=38, show="*",
        )
        self.entry_password_nuevo.pack(pady=5)

        self.entry_confirmar = ctk.CTkEntry(
            frame, placeholder_text="Confirmar nueva contraseña", width=300, height=38, show="*",
        )
        self.entry_confirmar.pack(pady=5)

        self.btn_cambiar = ctk.CTkButton(
            frame, text="Cambiar Contraseña", width=300, height=40,
            command=self._on_cambiar,
        )
        self.btn_cambiar.pack(pady=20)

        self.label_error = ctk.CTkLabel(
            frame, text="", font=ctk.CTkFont(size=12),
        )
        self.label_error.pack()

    def _on_cambiar(self):
        password_actual = self.entry_password_actual.get().strip()
        password_nuevo = self.entry_password_nuevo.get().strip()
        confirmar = self.entry_confirmar.get().strip()

        exito, mensaje = login_controller.cambiar_password(
            password_actual, password_nuevo, confirmar,
        )

        if exito:
            self.label_error.configure(text=mensaje, text_color="green")
            self.after(1000, self._abrir_siguiente)
        else:
            self.label_error.configure(text=mensaje, text_color="red")

    def _abrir_siguiente(self):
        if self.on_success:
            self.on_success()
        self.destroy()

    def _on_cerrar(self):
        from database.connection import close_connection
        close_connection()
        self.master.destroy()
