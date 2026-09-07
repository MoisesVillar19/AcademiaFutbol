import customtkinter as ctk

class PaginationBar(ctk.CTkFrame):
    def __init__(self, parent, on_page_change, per_page=50, *args, **kwargs):
        super().__init__(parent, fg_color="transparent", *args, **kwargs)
        self.on_page_change = on_page_change
        self.per_page = per_page
        self._total = 0
        self._create_widgets()

    def set_total(self, total):
        self._total = total
        self._update_buttons()

    def reset(self):
        self._page = 1
        self._update_buttons()

    def _create_widgets(self):
        self.frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frame.pack(fill="x", padx=5, pady=4)

        self.btn_first = ctk.CTkButton(self.frame, text="<<", width=30, command=self._first)
        self.btn_first.pack(side="left", padx=2)

        self.label_page = ctk.CTkLabel(self.frame, text="Página 1 de 1", font=ctk.CTkFont(size=11))
        self.label_page.pack(side="left", padx=10)

        self.btn_prev = ctk.CTkButton(self.frame, text="<", width=30, command=self._prev, state="disabled")
        self.btn_prev.pack(side="left", padx=2)

        self.btn_next = ctk.CTkButton(self.frame, text=">", width=30, command=self._next, state="disabled" if self._total <= self.per_page else "normal")
        self.btn_next.pack(side="left", padx=2)

        self.btn_last = ctk.CTkButton(self.frame, text=">>", width=30, command=self._last)
        self.btn_last.pack(side="left", padx=2)

    def _first(self):
        self._page = 1
        self._update_buttons()
        self.on_page_change(1, self.per_page)

    def _prev(self):
        if self._page > 1:
            self._page -= 1
            self._update_buttons()
            self.on_page_change(self._page, self.per_page)

    def _next(self):
        total_pages = max(1, (self._total + self.per_page - 1) // self.per_page)
        if self._page < total_pages:
            self._page += 1
            self._update_buttons()
            self.on_page_change(self._page, self.per_page)

    def _last(self):
        total_pages = max(1, (self._total + self.per_page - 1) // self.per_page)
        self._page = total_pages
        self._update_buttons()
        self.on_page_change(self._page, self.per_page)

    def _update_buttons(self):
        total_pages = max(1, (self._total + self.per_page - 1) // self.per_page)
        self.label_page.configure(text=f"Página {self._page} de {total_pages}")
        self.btn_next.configure(state="normal" if self._page < total_pages else "disabled")
        self.btn_prev.configure(state="normal" if self._page > 1 else "disabled")