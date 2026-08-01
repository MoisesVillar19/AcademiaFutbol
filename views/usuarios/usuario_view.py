import customtkinter as ctk
from controllers import usuario_controller
from controllers import login_controller


class UsuarioView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._crear_widgets()
        self._cargar_usuarios()

    def _crear_widgets(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            header, text="Gestión de Usuarios",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            header, text="+ Nuevo Usuario", width=150,
            command=self._abrir_formulario,
        ).pack(side="right")

        filtros = ctk.CTkFrame(self, fg_color="transparent")
        filtros.pack(fill="x", padx=10, pady=5)

        self.filtro_estado = ctk.CTkSegmentedButton(
            filtros, values=["Todos", "Activos", "Inactivos"],
            command=self._filtrar,
        )
        self.filtro_estado.set("Todos")
        self.filtro_estado.pack(side="left")

        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.label_status = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11))
        self.label_status.pack(pady=5)

    def _cargar_usuarios(self, activo=None):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        usuarios = usuario_controller.listar_usuarios(activo=activo)

        if not usuarios:
            ctk.CTkLabel(
                self.scroll_frame, text="No hay usuarios registrados",
                text_color="gray",
            ).pack(pady=20)
            return

        for usuario in usuarios:
            self._crear_card(usuario)

        self.label_status.configure(text=f"Total: {len(usuarios)} usuario(s)")

    def _crear_card(self, usuario):
        card = ctk.CTkFrame(self.scroll_frame)
        card.pack(fill="x", padx=5, pady=3)

        estado_color = "green" if usuario["activo"] else "red"
        estado_text = "Activo" if usuario["activo"] else "Inactivo"

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=10, pady=8)

        ctk.CTkLabel(
            info, text=f"{usuario['username']}",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            info, text=f"Rol: {usuario['rol']}  |  Estado: {estado_text}",
            font=ctk.CTkFont(size=12), text_color="gray",
        ).pack(anchor="w")

        botones = ctk.CTkFrame(card, fg_color="transparent")
        botones.pack(side="right", padx=5, pady=5)

        if usuario["activo"]:
            ctk.CTkButton(
                botones, text="Desactivar", width=90, height=30,
                fg_color="red", hover_color="darkred",
                command=lambda u=usuario: self._desactivar(u),
            ).pack(side="left", padx=2)
        else:
            ctk.CTkButton(
                botones, text="Activar", width=90, height=30,
                fg_color="green", hover_color="darkgreen",
                command=lambda u=usuario: self._activar(u),
            ).pack(side="left", padx=2)

        ctk.CTkButton(
            botones, text="Restablecer", width=100, height=30,
            fg_color="orange", hover_color="darkorange",
            command=lambda u=usuario: self._restablecer(u),
        ).pack(side="left", padx=2)

    def _filtrar(self, valor):
        if valor == "Activos":
            self._cargar_usuarios(activo=1)
        elif valor == "Inactivos":
            self._cargar_usuarios(activo=0)
        else:
            self._cargar_usuarios()

    def _abrir_formulario(self):
        dialog = ctk.CTkInputDialog(
            text="Ingrese el nombre de usuario:", title="Nuevo Usuario",
        )
        username = dialog.get_input()
        if not username:
            return

        dialog2 = ctk.CTkInputDialog(
            text="Ingrese el DNI de la persona:", title="DNI",
        )
        dni = dialog2.get_input()
        if not dni:
            return

        persona_data = {
            "dni": dni,
            "nombres": "",
            "apellidos": "",
        }

        dialog3 = ctk.CTkInputDialog(
            text="Rol (ADMIN o SECRETARIA):", title="Rol",
        )
        rol = dialog3.get_input()
        if not rol:
            return

        exito, mensaje, id_usuario = usuario_controller.crear_usuario(persona_data, username, rol)

        if exito:
            ctk.CTkLabel(
                self.scroll_frame,
                text=f"Usuario creado. Contraseña temporal: {mensaje}",
                text_color="green",
            ).pack(pady=5)
            self._cargar_usuarios()
        else:
            ctk.CTkLabel(
                self.scroll_frame, text=mensaje, text_color="red",
            ).pack(pady=5)

    def _activar(self, usuario):
        exito, mensaje = usuario_controller.activar_usuario(usuario["id_usuario"])
        if exito:
            self._cargar_usuarios()

    def _desactivar(self, usuario):
        exito, mensaje = usuario_controller.desactivar_usuario(usuario["id_usuario"])
        if exito:
            self._cargar_usuarios()

    def _restablecer(self, usuario):
        exito, mensaje, temp_pass = usuario_controller.restablecer_password(usuario["id_usuario"])
        if exito:
            ctk.CTkLabel(
                self.scroll_frame,
                text=f"Contraseña restablecida. Nueva contraseña temporal: {temp_pass}",
                text_color="green",
            ).pack(pady=5)
