"""Tela de Formulário (Modal) para gerar empréstimos com simulação, validações de score e garantias."""

from tkcalendar import DateEntry
import customtkinter as ctk
from tkinter import ttk, messagebox
from database.connection import SessionLocal
from services.emprestimo_service import EmprestimoService
from services.cliente_service import ClienteService

class EmprestimoFormView(ctk.CTkToplevel):
    def __init__(self, master, on_save_callback):
        super().__init__(master)
        
        self.on_save_callback = on_save_callback
        self.service = EmprestimoService()
        self.cliente_service = ClienteService()
        self.clientes = []
        self.parcelas_simuladas = []
        self.current_metrics = None
        
        self.title("Novo Empréstimo com Validação de Segurança")
        self.geometry("780x750")
        self.minsize(700, 600)
        self.resizable(True, True)
        
        # Centralizar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (780 // 2)
        y = (self.winfo_screenheight() // 2) - (750 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.grab_set()
        
        self._load_clientes()
        self._create_widgets()
        if self.clientes:
            self._on_cliente_selected(self.combo_cliente.get())

    def _load_clientes(self):
        db = SessionLocal()
        try:
            self.clientes = self.cliente_service.get_all(db)
        finally:
            db.close()

    def _create_widgets(self):
        # Frame Superior: Dados do Empréstimo
        top_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        top_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        lbl_titulo = ctk.CTkLabel(top_frame, text="Dados do Empréstimo e Garantias", font=ctk.CTkFont(size=18, weight="bold"))
        lbl_titulo.grid(row=0, column=0, columnspan=4, pady=(10, 15), sticky="w", padx=15)

        # 1. Seleção de Cliente
        ctk.CTkLabel(top_frame, text="Cliente *").grid(row=1, column=0, sticky="w", padx=15, pady=5)
        self.combo_cliente = ctk.CTkComboBox(
            top_frame, width=320, 
            values=[f"{c.id} - {c.nome}" for c in self.clientes],
            command=self._on_cliente_selected
        )
        self.combo_cliente.grid(row=1, column=1, columnspan=3, sticky="w", pady=5)

        # Label de Badge e Score do Cliente
        self.lbl_score_badge = ctk.CTkLabel(
            top_frame, text="", font=ctk.CTkFont(size=12, weight="bold"), 
            justify="left"
        )
        self.lbl_score_badge.grid(row=2, column=1, columnspan=3, sticky="w", pady=(0, 10))

        # 2. Valor Solicitado e Taxa
        ctk.CTkLabel(top_frame, text="Valor Solicitado (R$) *").grid(row=3, column=0, sticky="w", padx=15, pady=5)
        self.entry_valor = ctk.CTkEntry(top_frame, width=140)
        self.entry_valor.grid(row=3, column=1, sticky="w", pady=5)

        ctk.CTkLabel(top_frame, text="Taxa Juros (%) *").grid(row=3, column=2, sticky="w", padx=15, pady=5)
        self.entry_taxa = ctk.CTkEntry(top_frame, width=100)
        self.entry_taxa.grid(row=3, column=3, sticky="w", pady=5)

        # 3. Data de Vencimento
        ctk.CTkLabel(top_frame, text="Data Vencimento (DD/MM/AAAA) *").grid(row=4, column=0, sticky="w", padx=15, pady=5)
        self.entry_vencimento = DateEntry(top_frame, width=18, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy', font=('Arial', 12))
        self.entry_vencimento.grid(row=4, column=1, columnspan=3, sticky="w", pady=5)

        # 4. (Garantias removidas a pedido do cliente)

        # Botão Simular
        self.btn_simular = ctk.CTkButton(top_frame, text="Simular Parcelas", command=self._on_simular_click)
        self.btn_simular.grid(row=7, column=3, sticky="e", pady=15, padx=15)

        # Frame Inferior: Tabela de Simulação
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        ctk.CTkLabel(bottom_frame, text="Pré-visualização das Parcelas", font=ctk.CTkFont(weight="bold")).pack(pady=5)

        columns = ("vencimento", "capital", "juros", "valor")
        self.tree = ttk.Treeview(bottom_frame, columns=columns, show="headings", height=2, style="Treeview")
        self.tree.heading("vencimento", text="Vencimento")
        self.tree.heading("capital", text="Capital (R$)")
        self.tree.heading("juros", text="Juros (R$)")
        self.tree.heading("valor", text="Total (R$)")
        
        self.tree.column("vencimento", width=120, anchor="center")
        self.tree.column("capital", width=120, anchor="center")
        self.tree.column("juros", width=120, anchor="center")
        self.tree.column("valor", width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=15, pady=5)

        # Botões Rodapé
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="gray", command=self.destroy).pack(side="left", padx=10)
        self.btn_salvar = ctk.CTkButton(btn_frame, text="Aprovar e Salvar Empréstimo", state="disabled", fg_color="#00C853", hover_color="#00E676", command=self._on_salvar_click)
        self.btn_salvar.pack(side="right", padx=10)

    def _on_cliente_selected(self, cliente_str: str):
        """Atualiza informações de Score, Limite e Inadimplência do cliente selecionado."""
        if not cliente_str:
            return
        try:
            cliente_id = int(cliente_str.split(" - ")[0])
            db = SessionLocal()
            try:
                self.current_metrics = self.cliente_service.get_cliente_metrics(db, cliente_id)
                m = self.current_metrics
                
                lim_fmt = f"R$ {m['limite_disponivel']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                max_fmt = f"R$ {m['limite_max']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                
                status_inad = " ⚠️ INADIMPLENTE (PARCELAS EM ATRASO)" if m['has_inadimplencia'] else ""
                
                badge_text = (
                    f"Nível: {m['nivel']} | Limite Disponível: {lim_fmt} (Teto: {max_fmt}) | "
                    f"Risco: {m['icon_risco']} {m['nivel_risco']}{status_inad}"
                )
                
                cor = "#FF5252" if m['has_inadimplencia'] else m['cor_risco']
                self.lbl_score_badge.configure(text=badge_text, text_color=cor)
            finally:
                db.close()
        except Exception:
            pass

    def _get_form_data(self):
        try:
            cliente_str = self.combo_cliente.get()
            cliente_id = int(cliente_str.split(" - ")[0])
            valor = float(self.entry_valor.get().replace(",", "."))
            taxa = float(self.entry_taxa.get().replace(",", "."))
            
            data_vencimento = self.entry_vencimento.get_date()
            
            tipo_garantia = "SEM_GARANTIA"
            garantia_desc = ""
            promissoria = "NAO_EXIGIDA"
            return cliente_id, valor, taxa, data_vencimento, tipo_garantia, garantia_desc, promissoria
        except Exception:
            messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios corretamente (especialmente a data no formato DD/MM/AAAA).")
            return None

    def _on_simular_click(self):
        data = self._get_form_data()
        if not data:
            return
            
        _, valor, taxa, data_vencimento, _, _, _ = data
        self.parcelas_simuladas = self.service.simulate_installments(valor, taxa, data_vencimento)
        
        # Limpar grid
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for p in self.parcelas_simuladas:
            data_str = p["data_vencimento"].strftime("%d/%m/%Y")
            cap_str = f"R$ {p['capital']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            jur_str = f"R$ {p['juros']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            val_str = f"R$ {p['valor_atualizado']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            self.tree.insert("", "end", values=(data_str, cap_str, jur_str, val_str))
            
        self.btn_salvar.configure(state="normal")

    def _on_salvar_click(self):
        if not self.parcelas_simuladas:
            return
            
        data = self._get_form_data()
        if not data:
            return
            
        cliente_id, valor, taxa, data_vencimento, tipo_garantia, garantia_desc, promissoria = data
        
        db = SessionLocal()
        try:
            self.service.create_loan(
                db, cliente_id, valor, taxa, data_vencimento,
                tipo_garantia=tipo_garantia,
                garantia_desc=garantia_desc, promissoria_status=promissoria
            )
            messagebox.showinfo("Sucesso", "Empréstimo registrado com sucesso!")
            self.on_save_callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Bloqueio de Segurança", str(e))
        finally:
            db.close()
