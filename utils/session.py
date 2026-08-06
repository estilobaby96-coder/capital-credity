"""Gerenciamento de Sessão do Usuário logado (in-memory singleton)."""

from typing import Optional
from models.usuario import Usuario


class SessionManager:
    """
    Singleton que mantém o estado da sessão do usuário logado.
    Em uma aplicação desktop, a sessão é mantida em memória durante a execução.
    """

    _instance: Optional["SessionManager"] = None
    _current_user: Optional[Usuario] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def current_user(self) -> Optional[Usuario]:
        """Retorna o usuário logado ou None."""
        return self._current_user

    @property
    def is_logged_in(self) -> bool:
        """Verifica se há um usuário logado."""
        return self._current_user is not None

    @property
    def is_admin(self) -> bool:
        """Verifica se o usuário logado é administrador."""
        if self._current_user is None:
            return False
        return self._current_user.tipo == "ADMIN"

    def login(self, user: Usuario) -> None:
        """Registra o usuário na sessão."""
        self._current_user = user

    def logout(self) -> None:
        """Encerra a sessão do usuário."""
        self._current_user = None


# Instância global para acesso fácil
session_manager = SessionManager()
