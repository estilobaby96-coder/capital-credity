"""Listagem de Parcelas pendentes e busca de clientes para pagamentos."""

import customtkinter as ctk
from tkinter import ttk, messagebox
from database.connection import SessionLocal
from services.pagamento_service import PagamentoService
from services.cliente_service import ClienteService
from views.pagamentos.baixa_form_view import BaixaFormView


class PagamentoListView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.service = PagamentoService()
        self.cliente_service = ClienteService()
        self.clientes = []
        self.parcelas = []

        self._load_clientes()
        self._create_widgets()

    def _load_clientes(self):
        db = SessionLocal()
        try:
            self.clientes = self.cliente_service.get_all(db)
        finally:
            db.close()

    def _create_widgets(self):
        # Top bar: Título e Busca
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)
        
        lbl_titulo = ctk.CTkLabel(top_frame, text="Recebimento de Parcelas", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_titulo.pack(side="left")
        
        # Filtro de Cliente
        ctk.CTkLabel(top_frame, text="Selecione o Cliente:").pack(side="left", padx=(40, 10))
        self.combo_cliente = ctk.CTkComboBox(top_frame, width=300, values=["Selecione..."] + [f"{c.id} - {c.nome}" for c in self.clientes], command=self._on_cliente_selected)
        self.combo_cliente.pack(side="left")

        # Tabela (Treeview)
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        columns = ("id", "emprestimo", "numero", "vencimento", "valor", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")
        
        self.tree.heading("id", text="ID Parcela")
        self.tree.heading("emprestimo", text="Nº Contrato")
        self.tree.heading("numero", text="Nº Parcela")
        self.tree.heading("vencimento", text="Vencimento")
        self.tree.heading("valor", text="Valor Esperado")
        self.tree.heading("status", text="Status")
        
        self.tree.column("id", width=80, anchor="center")
        self.tree.column("emprestimo", width=120, anchor="center")
        self.tree.column("numero", width=100, anchor="center")
        self.tree.column("vencimento", width=120, anchor="center")
        self.tree.column("valor", width=150, anchor="center")
        self.tree.column("status", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<Double-1>", lambda e: self._on_baixa_click())

        # Rodapé
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        btn_wa = ctk.CTkButton(
            bottom_frame, text="📱 Cobrar WhatsApp", 
            fg_color="#25D366", hover_color="#1EBE5D", text_color="white",
            command=self._on_whatsapp_click
        )
        btn_wa.pack(side="left")

        btn_baixa = ctk.CTkButton(bottom_frame, text="Realizar Baixa (Receber)", fg_color="#00C853", hover_color="#00E676", command=self._on_baixa_click)
        btn_baixa.pack(side="right")

    def _on_whatsapp_click(self):
        parcela = self._get_selected_parcela()
        if not parcela:
            return

        db = SessionLocal()
        try:
            from models.cliente import Cliente
            from utils.whatsapp_helper import open_whatsapp_cobranca
            from datetime import date

            # Buscar o cliente do empréstimo
            emp = self.service.emprestimo_repo.get(db, parcela.emprestimo_id)
            if not emp:
                messagebox.showerror("Erro", "Empréstimo não encontrado.")
                return

            cliente = db.query(Cliente).filter(Cliente.id == emp.cliente_id).first()
            if not cliente or not (cliente.whatsapp or cliente.telefone):
                messagebox.showwarning("Aviso", f"O cliente '{cliente.nome if cliente else ''}' não possui telefone/WhatsApp cadastrado.")
                return

            phone = cliente.whatsapp or cliente.telefone
            
            # Tipo de mensagem
            hoje = date.today()
            venc = parcela.data_vencimento.date() if hasattr(parcela.data_vencimento, 'date') else parcela.data_vencimento
            
            if venc < hoje:
                tipo_msg = "ATRASO"
            elif venc == hoje:
                tipo_msg = "HOJE"
            else:
                tipo_msg = "LEMBRETE"

            res = open_whatsapp_cobranca(phone, cliente.nome, parcela.valor_atualizado, venc, tipo=tipo_msg)
            if not res:
                messagebox.showerror("Erro", "Telefone em formato inválido para disparo de WhatsApp.")
        finally:
            db.close()

    def _on_cliente_selected(self, choice):
        if choice == "Selecione...":
            self._clear_grid()
            return
            
        cliente_id = int(choice.split(" - ")[0])
        self._load_parcelas(cliente_id)

    def _clear_grid(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.parcelas = []

    def _load_parcelas(self, cliente_id: int):
        self._clear_grid()
        db = SessionLocal()
        try:
            self.parcelas = self.service.get_parcelas_pendentes_by_cliente(db, cliente_id)
            for p in self.parcelas:
                venc_str = p.data_vencimento.strftime("%d/%m/%Y")
                valor_str = f"R$ {p.valor_atualizado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                
                # Buscar o número do contrato
                contrato = ""
                if p.emprestimo:
                    contrato = p.emprestimo.numero_contrato or str(p.emprestimo_id)
                else:
                    contrato = str(p.emprestimo_id)
                
                self.tree.insert("", "end", iid=str(p.id), values=(
                    p.id, 
                    contrato, 
                    f"{p.numero}", 
                    venc_str, 
                    valor_str, 
                    p.status
                ))
        finally:
            db.close()

    def _get_selected_parcela(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma parcela na lista para realizar esta ação.")
            return None
        
        parcela_id = int(selected[0])
        for p in self.parcelas:
            if p.id == parcela_id:
                return p
        return None

    def _on_baixa_click(self):
        parcela = self._get_selected_parcela()
        if parcela:
            cliente_str = self.combo_cliente.get()
            if cliente_str != "Selecione...":
                cliente_id = int(cliente_str.split(" - ")[0])
                BaixaFormView(self.winfo_toplevel(), parcela, on_save_callback=lambda: self._load_parcelas(cliente_id))

