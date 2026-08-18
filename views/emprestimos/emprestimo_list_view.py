"""Listagem de Empréstimos (Grid) para a área central."""

import customtkinter as ctk
from tkinter import ttk
from database.connection import SessionLocal
from services.emprestimo_service import EmprestimoService
from views.emprestimos.emprestimo_form_view import EmprestimoFormView

class EmprestimoListView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.service = EmprestimoService()
        self.emprestimos = []

        self._create_widgets()
        self._load_data()

    def _create_widgets(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)
        
        lbl_titulo = ctk.CTkLabel(top_frame, text="Gestão de Empréstimos", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_titulo.pack(side="left")
        
        self.btn_novo = ctk.CTkButton(top_frame, text="+ Novo Empréstimo", command=self._on_novo_click)
        self.btn_novo.pack(side="right")
        
        # Tabela (Treeview)
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = ("contrato", "cliente", "data", "solicitado", "total", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")
        
        self.tree.heading("contrato", text="Nº Contrato")
        self.tree.heading("cliente", text="Cliente")
        self.tree.heading("data", text="Data")
        self.tree.heading("solicitado", text="Valor Solicitado")
        self.tree.heading("total", text="Valor Total")
        self.tree.heading("status", text="Status")
        
        self.tree.column("contrato", width=100, anchor="center")
        self.tree.column("cliente", width=250, anchor="center")
        self.tree.column("data", width=100, anchor="center")
        self.tree.column("solicitado", width=120, anchor="center")
        self.tree.column("total", width=120, anchor="center")
        self.tree.column("status", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        db = SessionLocal()
        try:
            self.emprestimos = self.service.get_all(db)
            for e in self.emprestimos:
                # Trata formatação
                data_str = e.criado_em.strftime("%d/%m/%Y") if e.criado_em else e.primeiro_vencimento.strftime("%d/%m/%Y")
                
                # A formatação do dinheiro R$ 0.000,00
                solicitado_str = f"R$ {e.valor_emprestado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                
                # Valor total seria o valor liberado + juros... Mas podemos usar o valor_emprestado aqui por hora,
                # já que o banco não armazena valor_total e podemos apenas mostrar o liberado na listagem.
                total_str = f"R$ {e.valor_liberado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                
                contrato = e.numero_contrato or f"#{e.id}"
                self.tree.insert("", "end", iid=str(e.id), values=(
                    contrato, 
                    e.cliente.nome if e.cliente else "Desconhecido", 
                    data_str, 
                    solicitado_str, 
                    total_str, 
                    e.status
                ))
        finally:
            db.close()

    def _on_novo_click(self):
        EmprestimoFormView(self.winfo_toplevel(), on_save_callback=self._load_data)
