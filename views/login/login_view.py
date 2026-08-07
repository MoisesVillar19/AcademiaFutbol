import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
from PIL import Image
from controllers import login_controller

COLOR_SIDEBAR  = "#3D1559"
COLOR_PRIMARY  = "#7C3AED"
COLOR_PRIMARY_H = "#6D28D9"
COLOR_BG       = "#F8F5FA"
COLOR_TEXT_SEC = "#6B5B7B"

ASSETS_DIR = Path(__file__).parent.parent.parent / "assets" / "images"


class RecuperarPasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Recuperar Contraseña")
        self.geometry("400x380")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        self.grab_set()
        self._centrar()
        self._crear_widgets()

    def _centrar(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 200
        y = (self.winfo_screenheight() // 2) - 190
        self.geometry(f"400x380+{x}+{y}")

    def _crear_widgets(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=30, pady=25)

        ctk.CTkLabel(
            frame, text="Recuperar Contraseña",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLOR_PRIMARY,
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            frame, text="Ingrese el PIN de emergencia y su nueva contraseña",
            font=ctk.CTkFont(size=11),
            text_color=COLOR_TEXT_SEC,
        ).pack(pady=(0, 15))

        ctk.CTkLabel(frame, text="PIN de emergencia *", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.entry_pin = ctk.CTkEntry(
            frame, placeholder_text="PIN", width=320, height=40, show="*",
            border_width=1, border_color="#ced4da", corner_radius=8,
        )
        self.entry_pin.pack(pady=(0, 10))

        ctk.CTkLabel(frame, text="Nueva contraseña *", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.entry_nueva = ctk.CTkEntry(
            frame, placeholder_text="Mínimo 6 caracteres", width=320, height=40, show="•",
            border_width=1, border_color="#ced4da", corner_radius=8,
        )
        self.entry_nueva.pack(pady=(0, 10))

        ctk.CTkLabel(frame, text="Confirmar contraseña *", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.entry_confirmar = ctk.CTkEntry(
            frame, placeholder_text="Repita la contraseña", width=320, height=40, show="•",
            border_width=1, border_color="#ced4da", corner_radius=8,
        )
        self.entry_confirmar.pack(pady=(0, 15))

        self.label_error = ctk.CTkLabel(
            frame, text="", text_color="#dc3545",
            font=ctk.CTkFont(size=11),
        )
        self.label_error.pack()

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=(5, 0))

        ctk.CTkButton(
            btn_frame, text="Cancelar", width=140, height=40,
            fg_color="#6c757d", hover_color="#5a6268",
            corner_radius=8, command=self.destroy,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, text="Restablecer", width=140, height=40,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_H,
            corner_radius=8, command=self._restablecer,
        ).pack(side="left", padx=5)

        self.entry_pin.bind("<Return>", lambda e: self.entry_nueva.focus())
        self.entry_nueva.bind("<Return>", lambda e: self.entry_confirmar.focus())
        self.entry_confirmar.bind("<Return>", lambda e: self._restablecer())
        self.entry_pin.focus()

    def _restablecer(self):
        pin = self.entry_pin.get().strip()
        nueva = self.entry_nueva.get().strip()
        confirmar = self.entry_confirmar.get().strip()

        if not pin:
            self.label_error.configure(text="Ingrese el PIN de emergencia")
            return

        if pin != "roncalli2026":
            self.label_error.configure(text="PIN incorrecto")
            return

        if len(nueva) < 6:
            self.label_error.configure(text="La contraseña debe tener al menos 6 caracteres")
            return

        if nueva != confirmar:
            self.label_error.configure(text="Las contraseñas no coinciden")
            return

        from services import usuario_service
        usuario = login_controller.obtener_usuario_actual()

        if not usuario:
            exito, msg, temp = usuario_service.restablecer_password(1)
            if exito:
                from utils.security import hash_password
                from database.connection import get_connection
                conn = get_connection()
                conn.execute(
                    "UPDATE usuario SET password_hash = ? WHERE username = ?",
                    (hash_password(nueva), "admin"),
                )
                conn.commit()
                messagebox.showinfo(
                    "Éxito",
                    "Contraseña restablecida correctamente.\n\n"
                    "Ahora puede iniciar sesión con su nueva contraseña.",
                )
                self.destroy()
            else:
                self.label_error.configure(text="Error al restablecer contraseña")
        else:
            from utils.security import hash_password
            from database.connection import get_connection
            conn = get_connection()
            conn.execute(
                "UPDATE usuario SET password_hash = ? WHERE id_usuario = ?",
                (hash_password(nueva), usuario["id_usuario"]),
            )
            conn.commit()
            messagebox.showinfo(
                "Éxito",
                "Contraseña restablecida correctamente.\n\n"
                "Ahora puede iniciar sesión con su nueva contraseña.",
            )
            self.destroy()


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

        self.btn_olvidar = ctk.CTkButton(
            frame, text="¿Olvidaste tu contraseña?",
            fg_color="transparent", hover_color="#e0e0e0",
            text_color=COLOR_TEXT_SEC,
            font=ctk.CTkFont(size=11, underline=True),
            width=200, height=30,
            command=self._mostrar_recuperar_password,
        )
        self.btn_olvidar.pack(pady=(5, 0))

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

    def _mostrar_recuperar_password(self):
        RecuperarPasswordDialog(self)

    def _on_cerrar(self):
        from database.connection import close_connection
        close_connection()
        self.master.destroy()
