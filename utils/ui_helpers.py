import customtkinter as ctk

# Paleta hover coherente (usada en toda la app)
HOVER_LIGHTEN = {
    "#7C3AED": "#8B5CF6",  # primario -> más claro
    "#6D28D9": "#7C3AED",
    "#3D1559": "#4E1D70",
    "#22C55E": "#4ADE80",
    "#DC2626": "#EF4444",
    "gray": "#6B7280",
    "#d9534f": "#e57373",
}

def _hex_lighten(hex_color: str, amount: int = 20) -> str:
    """Aclara un color hex para hover (sin dependencias)."""
    try:
        hex_color = hex_color.lstrip("#")
        r = min(255, int(hex_color[0:2], 16) + amount)
        g = min(255, int(hex_color[2:4], 16) + amount)
        b = min(255, int(hex_color[4:6], 16) + amount)
        return f"#{r:02X}{g:02X}{b:02X}"
    except Exception:
        return hex_color

def crear_boton_interactivo(parent, text, command, fg_color="#7C3AED", width=120, height=32, **kwargs):
    """CTkButton con hover visible, cursor mano y feedback pressed."""
    hover = kwargs.pop("hover_color", None)
    if hover is None:
        hover = HOVER_LIGHTEN.get(fg_color, _hex_lighten(fg_color, 22))
    btn = ctk.CTkButton(
        parent, text=text, command=command,
        fg_color=fg_color, hover_color=hover,
        width=width, height=height,
        corner_radius=8,
        **kwargs
    )
    # cursor mano + feedback pressed (ligero scale visual)
    try:
        btn.bind("<Enter>", lambda e: btn.configure(cursor="hand2"))
        btn.bind("<Leave>", lambda e: btn.configure(cursor=""))
        # pressed effect: oscurece levemente
        btn.bind("<ButtonPress-1>", lambda e: btn.configure(fg_color=hover))
        btn.bind("<ButtonRelease-1>", lambda e: btn.configure(fg_color=fg_color))
    except Exception:
        pass
    return btn


def crear_card_interactiva(parent, hover_bg="#F3E8FF", border_hover="#DDD6E5"):
    """Frame que resalta al pasar el mouse (para distinguir estático vs interactivo)."""
    frame = ctk.CTkFrame(parent, fg_color="white", border_width=1, border_color="#E5E7EB")
    try:
        orig = frame.cget("fg_color")
        orig_border = frame.cget("border_color")
        frame.bind("<Enter>", lambda e: frame.configure(fg_color=hover_bg, border_color=border_hover, cursor="hand2"))
        frame.bind("<Leave>", lambda e: frame.configure(fg_color=orig, border_color=orig_border, cursor=""))
        # propagar a hijos para que no pierda hover al pasar sobre labels internos
        def _bind_children(w):
            for ch in w.winfo_children():
                try:
                    ch.bind("<Enter>", lambda e: frame.configure(fg_color=hover_bg, border_color=border_hover, cursor="hand2"))
                    ch.bind("<Leave>", lambda e: frame.configure(fg_color=orig, border_color=orig_border, cursor=""))
                except Exception:
                    pass
                _bind_children(ch)
        # se bindea lazy tras pack
        frame.after(100, lambda: _bind_children(frame))
    except Exception:
        pass
    return frame
