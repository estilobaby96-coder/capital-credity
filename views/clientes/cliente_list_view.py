"""Listagem de Clientes (Grid) para a área central."""

import customtkinter as ctk
from tkinter import ttk, messagebox
from database.connection import SessionLocal
from services.cliente_service import ClienteService
from views.clientes.cliente_form_view import ClienteFormView

class ClienteListView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.service = ClienteService()
        self.clientes = []

        self._create_widgets()
        self._load_data()

    def _create_widgets(self):
        # Top bar: Título, Busca e Botão Novo
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)
        
        lbl_titulo = ctk.CTkLabel(top_frame, text="Gerenciar Clientes", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_titulo.pack(side="left")
        
        self.btn_novo = ctk.CTkButton(top_frame, text="+ Novo Cliente", command=self._on_novo_click)
        self.btn_novo.pack(side="right")
        
        self.entry_busca = ctk.CTkEntry(top_frame, placeholder_text="Buscar cliente...", width=250)
        self.entry_busca.pack(side="right", padx=10)
        self.entry_busca.bind("<Return>", lambda e: self._load_data(self.entry_busca.get()))

        # Configurar estilo do Treeview para combinar com Dark Mode
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2a2d2e",
                        foreground="white",
                        rowheight=35,
                        fieldbackground="#343638",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading",
                        background="#565b5e",
                        foreground="white",
                        relief="flat",
                        font=("Roboto", 10, "bold"))
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

        # Tabela (Treeview)
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = ("id", "nome", "cpf", "telefone", "score", "risco")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("cpf", text="CPF")
        self.tree.heading("telefone", text="Telefone")
        self.tree.heading("score", text="Nível (Score)")
        self.tree.heading("risco", text="Termômetro de Risco")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nome", width=220, anchor="center")
        self.tree.column("cpf", width=110, anchor="center")
        self.tree.column("telefone", width=110, anchor="center")
        self.tree.column("score", width=120, anchor="center")
        self.tree.column("risco", width=150, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<Double-1>", self._on_double_click)

        # Botões de ação (Rodapé)
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        btn_editar = ctk.CTkButton(bottom_frame, text="Editar Selecionado", command=self._on_editar_click)
        btn_editar.pack(side="left")

        btn_ver_score = ctk.CTkButton(bottom_frame, text="🔍 Detalhes do Score/Risco", fg_color="#29B6F6", hover_color="#0288D1", command=self._on_ver_score_click)
        btn_ver_score.pack(side="left", padx=10)
        
        btn_excluir = ctk.CTkButton(bottom_frame, text="Excluir Selecionado", fg_color="#FF5252", hover_color="#D50000", command=self._on_excluir_click)
        btn_excluir.pack(side="left")

    def _load_data(self, search_term=""):
        # Limpar grid
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        db = SessionLocal()
        try:
            self.clientes = self.service.search(db, search_term)
            for c in self.clientes:
                metrics = self.service.get_cliente_metrics(db, c.id)
                nivel_str = f"🏅 {metrics['nivel']}"
                risco_str = f"{metrics['icon_risco']} {metrics['nivel_risco']}"
                
                self.tree.insert("", "end", iid=str(c.id), values=(
                    c.id, c.nome, c.cpf, c.telefone or "-", nivel_str, risco_str
                ))
        finally:
            db.close()

    def _on_ver_score_click(self):
        cliente = self._get_selected_cliente()
        if not cliente:
            return
            
        db = SessionLocal()
        try:
            m = self.service.get_cliente_metrics(db, cliente.id)
            lim_fmt = f"R$ {m['limite_disponivel']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            max_fmt = f"R$ {m['limite_max']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            uso_fmt = f"R$ {m['saldo_utilizado']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            msg = (
                f"📊 PERFIL DE CRÉDITO E RISCO — {cliente.nome}\n\n"
                f"• Nível do Score: {m['nivel']} ({m['qtd_quitados']} empréstimos quitados em dia)\n"
                f"• Limite Total do Nível: {max_fmt}\n"
                f"• Empréstimos Ativos em Uso: {uso_fmt}\n"
                f"• Limite Disponível para Novo Empréstimo: {lim_fmt}\n\n"
                f"🌡️ TERMÔMETRO DE RISCO: {m['icon_risco']} {m['nivel_risco']}\n"
                f"• Taxa de Pontualidade: {m['taxa_pontualidade']}%\n"
                f"• Total de Rolagens (Juros): {m['total_rolagens']} vez(es)\n"
                f"• Parcelas Atrasadas: {m['qtd_parcelas_atrasadas']}"
            )
            messagebox.showinfo("Perfil de Crédito & Risco", msg)
        finally:
            db.close()

    def _get_selected_cliente(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um cliente na lista primeiro.")
            return None
        
        cliente_id = int(selected[0])
        # Achar na lista
        for c in self.clientes:
            if c.id == cliente_id:
                return c
        return None

    def _on_novo_click(self):
        ClienteFormView(self.winfo_toplevel(), on_save_callback=self._load_data)

    def _on_editar_click(self):
        cliente = self._get_selected_cliente()
        if cliente:
            ClienteFormView(self.winfo_toplevel(), on_save_callback=self._load_data, cliente=cliente)

    def _on_double_click(self, event):
        self._on_editar_click()

    def _on_excluir_click(self):
        cliente = self._get_selected_cliente()
        if not cliente:
            return
            
        if messagebox.askyesno("Confirmação", f"Tem certeza que deseja excluir o cliente '{cliente.nome}'?"):
            db = SessionLocal()
            try:
                self.service.delete(db, cliente.id)
                messagebox.showinfo("Sucesso", "Cliente excluído com sucesso.")
                self._load_data()
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao excluir:\n{str(e)}")
            finally:
                db.close()
