import customtkinter as ctk
from tkinter import messagebox
from database.connection import SessionLocal
from services.auth_service import AuthService
from utils.session import session_manager
from config.settings import COLOR_SURFACE, FONT_SIZE_H1

class ConfiguracaoView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.auth_service = AuthService()
        self._create_widgets()

    def _create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(header, text="Configurações", font=ctk.CTkFont(size=FONT_SIZE_H1, weight="bold")).pack(side="left")

        # Painel central
        panel = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=12)
        panel.pack(fill="x", padx=20, pady=(0, 10))

        # Título da seção
        ctk.CTkLabel(
            panel, 
            text="Alterar Senha do Usuário Logado", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Campos
        self.entry_senha_atual = ctk.CTkEntry(panel, width=300, show="*", placeholder_text="Senha Atual")
        self.entry_senha_atual.pack(anchor="w", padx=20, pady=(10, 0))

        self.entry_nova_senha = ctk.CTkEntry(panel, width=300, show="*", placeholder_text="Nova Senha")
        self.entry_nova_senha.pack(anchor="w", padx=20, pady=(15, 0))

        self.entry_confirma_senha = ctk.CTkEntry(panel, width=300, show="*", placeholder_text="Confirmar Nova Senha")
        self.entry_confirma_senha.pack(anchor="w", padx=20, pady=(15, 20))

        btn_salvar = ctk.CTkButton(panel, text="💾 Salvar Nova Senha", command=self._alterar_senha)
        btn_salvar.pack(anchor="w", padx=20, pady=(0, 20))

    def _alterar_senha(self):
        senha_atual = self.entry_senha_atual.get().strip()
        nova_senha = self.entry_nova_senha.get().strip()
        confirma_senha = self.entry_confirma_senha.get().strip()

        if not all([senha_atual, nova_senha, confirma_senha]):
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        if nova_senha != confirma_senha:
            messagebox.showwarning("Aviso", "A nova senha e a confirmação não coincidem.")
            return

        usuario_logado = session_manager.current_user
        if not usuario_logado:
            messagebox.showerror("Erro", "Nenhum usuário logado.")
            return

        db = SessionLocal()
        try:
            # Verifica a senha atual
            if not self.auth_service.verificar_senha(senha_atual, usuario_logado.senha_hash):
                messagebox.showerror("Erro", "A senha atual está incorreta.")
                return

            # Altera para a nova senha
            novo_hash = self.auth_service.hash_senha(nova_senha)
            # Rebuscar o objeto atachado à sessão atual
            from models.usuario import Usuario
            u = db.query(Usuario).filter(Usuario.id == usuario_logado.id).first()
            if u:
                u.senha_hash = novo_hash
                db.commit()
                # Atualizar a sessão
                session_manager.current_user.senha_hash = novo_hash
                messagebox.showinfo("Sucesso", "Senha alterada com sucesso!")
                
                # Limpar campos
                self.entry_senha_atual.delete(0, 'end')
                self.entry_nova_senha.delete(0, 'end')
                self.entry_confirma_senha.delete(0, 'end')
            else:
                messagebox.showerror("Erro", "Usuário não encontrado no banco de dados.")

        except Exception as e:
            db.rollback()
            messagebox.showerror("Erro", f"Ocorreu um erro ao alterar a senha:\n{str(e)}")
        finally:
            db.close()
