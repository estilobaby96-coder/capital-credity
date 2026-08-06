"""Tela de Login — Interface moderna com CustomTkinter."""

import os
import customtkinter as ctk
from PIL import Image
from config.settings import (
    COLOR_BACKGROUND, COLOR_SURFACE, COLOR_PRIMARY,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, FONT_SIZE_H1, FONT_SIZE_BODY
)


class LoginView(ctk.CTkToplevel):
    """Tela de Login corporativa da Capital Credity."""

    def __init__(self, master, on_login_success):
        super().__init__(master)

        self.on_login_success = on_login_success

        # Configurações da janela
        self.title("Capital Credity - Login")
        self.geometry("500x700")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BACKGROUND)

        # Centralizar na tela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"500x700+{x}+{y}")

        # Impedir interação com a janela principal
        self.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        """Monta todos os widgets da tela de login."""

        # Frame central com bordas arredondadas
        self.login_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=15, width=400, height=620)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.login_frame.pack_propagate(False)

        # Logo
        from utils.resource_path import get_resource_path
        logo_path = get_resource_path(os.path.join("assets", "logo", "logo.png"))
        if os.path.exists(logo_path):
            logo_img = ctk.CTkImage(Image.open(logo_path), size=(200, 200))
            logo_label = ctk.CTkLabel(self.login_frame, text="", image=logo_img)
            logo_label.pack(pady=(30, 5))
        else:
            logo_label = ctk.CTkLabel(
                self.login_frame, text="Capital Credity",
                font=ctk.CTkFont(size=FONT_SIZE_H1, weight="bold"),
                text_color=COLOR_PRIMARY
            )
            logo_label.pack(pady=(30, 5))

        # Subtítulo
        subtitle = ctk.CTkLabel(
            self.login_frame, text="Gestor Financeiro de Empréstimos",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_SECONDARY
        )
        subtitle.pack(pady=(0, 25))

        # Campo Usuário
        user_label = ctk.CTkLabel(
            self.login_frame, text="Usuário",
            font=ctk.CTkFont(size=FONT_SIZE_BODY),
            text_color=COLOR_TEXT_PRIMARY, anchor="w"
        )
        user_label.pack(padx=40, pady=(10, 2), anchor="w")

        self.entry_usuario = ctk.CTkEntry(
            self.login_frame, placeholder_text="Digite seu usuário",
            width=320, height=40, corner_radius=8
        )
        self.entry_usuario.pack(padx=40)

        # Campo Senha
        pwd_label = ctk.CTkLabel(
            self.login_frame, text="Senha",
            font=ctk.CTkFont(size=FONT_SIZE_BODY),
            text_color=COLOR_TEXT_PRIMARY, anchor="w"
        )
        pwd_label.pack(padx=40, pady=(15, 2), anchor="w")

        self.entry_senha = ctk.CTkEntry(
            self.login_frame, placeholder_text="Digite sua senha",
            width=320, height=40, corner_radius=8, show="●"
        )
        self.entry_senha.pack(padx=40)

        # Checkbox Mostrar Senha
        self.show_password_var = ctk.BooleanVar(value=False)
        self.chk_show_password = ctk.CTkCheckBox(
            self.login_frame, text="Mostrar senha",
            variable=self.show_password_var,
            command=self._toggle_password,
            font=ctk.CTkFont(size=11),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.chk_show_password.pack(padx=40, pady=(8, 0), anchor="w")

        # Label de erro (invisível até ser necessário)
        self.error_label = ctk.CTkLabel(
            self.login_frame, text="",
            font=ctk.CTkFont(size=12),
            text_color="#FF5252"
        )
        self.error_label.pack(pady=(10, 0))

        # Botão Entrar
        self.btn_login = ctk.CTkButton(
            self.login_frame, text="Entrar",
            width=320, height=42, corner_radius=8,
            font=ctk.CTkFont(size=FONT_SIZE_BODY, weight="bold"),
            command=self._on_login_click
        )
        self.btn_login.pack(padx=40, pady=(15, 10))

        # Bind Enter key
        self.entry_senha.bind("<Return>", lambda e: self._on_login_click())
        self.entry_usuario.bind("<Return>", lambda e: self.entry_senha.focus())

        # Foco inicial no campo de usuário
        self.after(100, lambda: self.entry_usuario.focus())

    def _toggle_password(self):
        """Alterna visibilidade da senha."""
        if self.show_password_var.get():
            self.entry_senha.configure(show="")
        else:
            self.entry_senha.configure(show="●")

    def _on_login_click(self):
        """Chamado ao clicar em Entrar."""
        login = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()

        if not login or not senha:
            self.error_label.configure(text="Preencha todos os campos.")
            return

        # Delega a autenticação ao callback
        self.on_login_success(login, senha, self)

    def show_error(self, message: str):
        """Exibe mensagem de erro na tela."""
        self.error_label.configure(text=message)
