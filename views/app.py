"""App — Orquestrador da aplicação. Controla o fluxo Login → Dashboard."""

import customtkinter as ctk
from database.connection import SessionLocal
from services.auth_service import AuthService
from utils.session import session_manager
from views.login_view import LoginView
from views.base_window import BaseWindow


class App(ctk.CTk):
    """Janela raiz invisível que orquestra o fluxo de login e a janela principal."""

    def __init__(self):
        super().__init__()

        # Janela raiz fica escondida — ela só serve para gerenciar o ciclo de vida
        self.withdraw()

        self.auth_service = AuthService()

        # Abre a tela de login
        self._show_login()

    def _show_login(self):
        """Exibe a tela de login como modal."""
        self.login_view = LoginView(self, on_login_success=self._handle_login)

    def _handle_login(self, login: str, senha: str, login_window: LoginView):
        """Callback chamado pelo LoginView quando o usuário clica em Entrar."""
        db = SessionLocal()
        try:
            user = self.auth_service.authenticate(db, login, senha)
            if user is None:
                login_window.show_error("Usuário ou senha inválidos.")
                return

            # Login bem-sucedido: registrar sessão
            session_manager.login(user)
            print(f"[AUTH] Usuário '{user.nome}' logado com sucesso. Tipo: {user.tipo}")

            # Fechar tela de login
            login_window.grab_release()
            login_window.destroy()

            import tkinter.messagebox as messagebox
            messagebox.showinfo("Bem-vindo", f"Olá, {user.nome}! Seja bem-vindo ao Capital Credity.")

            # Abrir janela principal
            self._show_main_window()

        finally:
            db.close()

    def _show_main_window(self):
        """Cria e exibe a janela principal (BaseWindow) como toplevel."""
        self.main_window = BaseWindow()
        self.main_window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        """Chamado ao fechar a janela principal."""
        session_manager.logout()
        self.main_window.destroy()
        self.destroy()
