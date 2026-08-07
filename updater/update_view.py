import customtkinter as ctk
import threading
from updater import update_service


class ActualizarDialog(ctk.CTkToplevel):
    def __init__(self, parent, info_actualizacion: dict):
        super().__init__(parent)
        self.info = info_actualizacion
        self.title("Actualizar AcademiaFutbol")
        self.geometry("420x320")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_cerrar)
        self.grab_set()
        self._centrar()
        self._construir_ui()

    def _centrar(self):
        self.update_idletasks()
        ancho = 420
        alto = 320
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _construir_ui(self):
        frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="Nueva versión disponible",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#7C3AED",
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            frame,
            text=f"Versión actual: {self._version_actual()}",
            font=ctk.CTkFont(size=13),
            text_color="#6B5B7B",
        ).pack(pady=(0, 2))

        ctk.CTkLabel(
            frame,
            text=f"Nueva versión: v{self.info['version']}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#22C55E",
        ).pack(pady=(0, 10))

        desc = self.info.get("descripcion", "Sin descripción")
        if len(desc) > 200:
            desc = desc[:200] + "..."
        ctk.CTkLabel(
            frame,
            text=desc,
            font=ctk.CTkFont(size=11),
            text_color="#6B5B7B",
            wraplength=360,
            justify="left",
        ).pack(pady=(0, 15))

        self._barra_progreso = ctk.CTkProgressBar(frame, width=360)
        self._barra_progreso.pack(pady=(0, 5))
        self._barra_progreso.set(0)

        self._label_estado = ctk.CTkLabel(
            frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#6B5B7B",
        )
        self._label_estado.pack(pady=(0, 10))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text="Ahora no",
            width=120,
            height=35,
            fg_color="#DDD6E5",
            hover_color="#c0c8d4",
            text_color="#1F0A33",
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            command=self._on_rechazar,
        ).pack(side="left", padx=(0, 10))

        self._btn_actualizar = ctk.CTkButton(
            btn_frame,
            text="Actualizar",
            width=120,
            height=35,
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
            command=self._on_actualizar,
        )
        self._btn_actualizar.pack(side="right")

    def _version_actual(self):
        from utils.constants import __version__
        return __version__

    def _on_actualizar(self):
        self._btn_actualizar.configure(state="disabled", text="Descargando...")
        self._label_estado.configure(text="Descargando actualización...")

        def _descargar():
            def callback_progreso(bytes_read, total):
                if total > 0:
                    progreso = bytes_read / total
                    self.after(0, lambda: self._barra_progreso.set(progreso))
                    porcentaje = int(progreso * 100)
                    self.after(0, lambda: self._label_estado.configure(
                        text=f"Descargando... {porcentaje}%"
                    ))

            exito = update_service.descargar_y_actualizar(
                self.info["url_descarga"],
                callback_progreso=callback_progreso,
            )
            if exito:
                self.after(0, self._on_descarga_completada)
            else:
                self.after(0, self._on_descarga_fallo)

        threading.Thread(target=_descargar, daemon=True).start()

    def _on_descarga_completada(self):
        self._label_estado.configure(
            text="Descarga completada. Reiniciando..."
        )
        self._barra_progreso.set(1)
        self.after(1000, update_service.reiniciar_app)

    def _on_descarga_fallo(self):
        self._btn_actualizar.configure(state="normal", text="Reintentar")
        self._label_estado.configure(
            text="Error al descargar. Intente nuevamente."
        )
        self._barra_progreso.set(0)

    def _on_rechazar(self):
        update_service.registrar_rechazo(self.info["version"])
        self.destroy()

    def _on_cerrar(self):
        update_service.registrar_rechazo(self.info["version"])
        self.destroy()


def verificar_y_mostrar(parent) -> None:
    def _verificar():
        info = update_service.verificar_actualizacion()
        if info:
            parent.after(0, lambda: ActualizarDialog(parent, info))
        else:
            update_service.registrar_verificacion()

    if update_service.debe_verificar():
        threading.Thread(target=_verificar, daemon=True).start()
