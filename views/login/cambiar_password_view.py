import customtkinter as ctk
from controllers import login_controller

COLOR_PRIMARY   = "#1f6aa5"
COLOR_PRIMARY_H = "#155a85"
COLOR_BG        = "#e8edf2"
COLOR_TEXT_SEC  = "#6c757d"


class CambiarPasswordView(ctk.CTkToplevel):
    def __init__(self, parent, on_success=None):
        super().__init__(parent)
        self.title("Cambiar Contraseña - Primer Acceso")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        self.protocol("WM_DELETE_WINDOW", self._on_cerrar)
        self.on_success = on_success
        self.transient(parent)
        self.grab_set()
        self.attributes("-topmost", True)
        self._crear_widgets()
        self._centrar_ventana()
        self.after(100, self._elevar)
        self.after(500, lambda: self.attributes("-topmost", False))

    def _elevar(self):
        try:
            self.lift()
            self.focus_force()
            self.grab_set()
            self.attributes("-topmost", True)
        except Exception:
            pass

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = 440
        alto = 460
        # centrado respecto al padre, no solo pantalla
        try:
            px = self.master.winfo_x()
            py = self.master.winfo_y()
            pw = self.master.winfo_width()
            ph = self.master.winfo_height()
            x = px + (pw - ancho)//2
            y = py + (ph - alto)//2
            # fallback si padre aún 1x1
            if pw < 100:
                x = (self.winfo_screenwidth() // 2) - (ancho // 2)
                y = (self.winfo_screenheight() // 2) - (alto // 2)
        except Exception:
            x = (self.winfo_screenwidth() // 2) - (ancho // 2)
            y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _crear_widgets(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=40, pady=30)

        ctk.CTkLabel(
            frame, text="🔒",
            font=ctk.CTkFont(size=48),
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            frame, text="Cambiar Contraseña",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLOR_PRIMARY,
        ).pack(pady=(0, 3))

        ctk.CTkLabel(
            frame, text="Es su primer acceso. Debe cambiar la contraseña.",
            font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_SEC,
        ).pack(pady=(0, 20))

        self.entry_password_actual = ctk.CTkEntry(
            frame, placeholder_text="Contraseña actual", width=320, height=42, show="*",
            border_width=1, border_color="#ced4da", corner_radius=10,
        )
        self.entry_password_actual.pack(pady=6)

        self.entry_password_nuevo = ctk.CTkEntry(
            frame, placeholder_text="Nueva contraseña (mín. 6 caracteres)", width=320, height=42, show="*",
            border_width=1, border_color="#ced4da", corner_radius=10,
        )
        self.entry_password_nuevo.pack(pady=6)

        self.entry_confirmar = ctk.CTkEntry(
            frame, placeholder_text="Confirmar nueva contraseña", width=320, height=42, show="*",
            border_width=1, border_color="#ced4da", corner_radius=10,
        )
        self.entry_confirmar.pack(pady=6)

        self.btn_cambiar = ctk.CTkButton(
            frame, text="Cambiar Contraseña", width=320, height=44,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_H,
            command=self._on_cambiar,
        )
        self.btn_cambiar.pack(pady=(18, 10))

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
