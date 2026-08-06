import os
import customtkinter as ctk
from PIL import Image
from config.settings import WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_BACKGROUND, COLOR_SURFACE
from utils.session import session_manager

class BaseWindow(ctk.CTkToplevel):
    """Janela principal do sistema, exibida após login bem-sucedido."""

    def __init__(self):
        super().__init__()

        user_name = session_manager.current_user.nome if session_manager.current_user else "Usuário"
        self.title(f"Capital Credity  |  {user_name}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(800, 600)
        self.after(0, lambda: self.state("zoomed"))
        
        # Grid layout (1 row, 2 columns)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._create_sidebar()
        self._create_main_area()


    def _create_sidebar(self):
        """Creates the navigation sidebar."""
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=COLOR_SURFACE)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        # Carregar logo
        from utils.resource_path import get_resource_path
        logo_path = get_resource_path(os.path.join("assets", "logo", "logo.png"))
        if os.path.exists(logo_path):
            self.logo_image = ctk.CTkImage(Image.open(logo_path), size=(200, 200))
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="", image=self.logo_image)
            self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        else:
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Capital Credity", font=ctk.CTkFont(size=24, weight="bold"))
            self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Botões de Navegação (Exemplo)
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_dashboard)
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        self.btn_clientes = ctk.CTkButton(self.sidebar_frame, text="Clientes", command=self.show_clientes)
        self.btn_clientes.grid(row=2, column=0, padx=20, pady=10)

        self.btn_emprestimos = ctk.CTkButton(self.sidebar_frame, text="Empréstimos", command=self.show_emprestimos)
        self.btn_emprestimos.grid(row=3, column=0, padx=20, pady=10)

        self.btn_recebimentos = ctk.CTkButton(self.sidebar_frame, text="Recebimentos", command=self.show_recebimentos)
        self.btn_recebimentos.grid(row=4, column=0, padx=20, pady=10)

        self.btn_relatorios = ctk.CTkButton(self.sidebar_frame, text="Relatórios", command=self.show_relatorios)
        self.btn_relatorios.grid(row=5, column=0, padx=20, pady=10)

        self.btn_configuracoes = ctk.CTkButton(self.sidebar_frame, text="Configurações", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.show_configuracoes)
        self.btn_configuracoes.grid(row=6, column=0, padx=20, pady=10)

        # Botão Sair
        self.btn_sair = ctk.CTkButton(self.sidebar_frame, text="Sair do Sistema", fg_color="#C0392B", hover_color="#922B21", command=self.logout)
        self.btn_sair.grid(row=8, column=0, padx=20, pady=20)

    def logout(self):
        """Efetua logout e fecha a aplicação ou volta para a tela de login."""
        user_name = session_manager.current_user.nome if session_manager.current_user else "Usuário"
        from tkinter import messagebox
        messagebox.showinfo("Até logo", f"Desconectado com sucesso. Até logo, {user_name}!")
        
        session_manager.logout()
        if hasattr(self.master, '_show_login'):
            self.master._show_login()
        self.destroy()
        
    def _create_main_area(self):
        """Creates the main content area."""
        self.main_frame = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.title_label = ctk.CTkLabel(self.main_frame, text="Bem-vindo ao Capital Credity", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=50)

    # Métodos de placeholder para a navegação
    def _clear_main_area(self):
        """Remove todos os widgets da área principal."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self._clear_main_area()
        from views.dashboard.dashboard_view import DashboardView
        
        dashboard = DashboardView(self.main_frame, fg_color="transparent")
        dashboard.pack(fill="both", expand=True)

    def show_clientes(self):
        self._clear_main_area()
        from views.clientes.cliente_list_view import ClienteListView
        
        # Renderiza a listagem preenchendo toda a área central
        cliente_view = ClienteListView(self.main_frame, fg_color="transparent")
        cliente_view.pack(fill="both", expand=True)

    def show_emprestimos(self):
        self._clear_main_area()
        from views.emprestimos.emprestimo_list_view import EmprestimoListView
        
        emprestimo_view = EmprestimoListView(self.main_frame, fg_color="transparent")
        emprestimo_view.pack(fill="both", expand=True)

    def show_recebimentos(self):
        self._clear_main_area()
        from views.pagamentos.pagamento_list_view import PagamentoListView
        
        pagamento_view = PagamentoListView(self.main_frame, fg_color="transparent")
        pagamento_view.pack(fill="both", expand=True)

    def show_relatorios(self):
        self._clear_main_area()
        from views.relatorios.relatorio_view import RelatorioView
        
        relatorio_view = RelatorioView(self.main_frame, fg_color="transparent")
        relatorio_view.pack(fill="both", expand=True)

    def show_configuracoes(self):
        self._clear_main_area()
        from views.configuracoes.configuracao_view import ConfiguracaoView
        
        config_view = ConfiguracaoView(self.main_frame, fg_color="transparent")
        config_view.pack(fill="both", expand=True)
