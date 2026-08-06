"""Tela de Relatórios — Seleção de tipo, filtros, pré-visualização, Controle Mensal e exportação."""

from datetime import date, datetime
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from database.connection import SessionLocal
from services.relatorio_service import RelatorioService
from services.cliente_service import ClienteService
from services.export_service import ExportService
from config.settings import COLOR_PRIMARY, COLOR_SURFACE, COLOR_TEXT_SECONDARY, FONT_SIZE_H1, FONT_SIZE_BODY


TIPOS_RELATORIO = [
    "Controle Mensal (Previsto vs. Realizado)",
    "Extrato do Cliente",
    "Inadimplência",
    "Fluxo de Caixa",
]

MESES_NOME = [
    "01 - Janeiro", "02 - Fevereiro", "03 - Março", "04 - Abril",
    "05 - Maio", "06 - Junho", "07 - Julho", "08 - Agosto",
    "09 - Setembro", "10 - Outubro", "11 - Novembro", "12 - Dezembro"
]


class RelatorioView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.rel_service = RelatorioService()
        self.cli_service = ClienteService()
        self.export_service = ExportService()
        self.clientes = []
        
        # Estado interno
        self._colunas_atuais = []
        self._dados_atuais = []
        self._titulo_atual = ""
        self._subtitulo_atual = ""
        
        self._load_clientes()
        self._create_widgets()

    def _load_clientes(self):
        db = SessionLocal()
        try:
            self.clientes = self.cli_service.get_all(db)
        finally:
            db.close()

    def _create_widgets(self):
        # ── Cabeçalho ──
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(header, text="Relatórios & Controle Mensal", font=ctk.CTkFont(size=FONT_SIZE_H1, weight="bold")).pack(side="left")

        # ── Painel de Filtros ──
        filtros = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=12)
        filtros.pack(fill="x", padx=20, pady=(0, 10))

        # Row 0: Tipo e Cliente
        ctk.CTkLabel(filtros, text="Tipo de Relatório:").grid(row=0, column=0, padx=(20, 8), pady=10, sticky="w")
        self.combo_tipo = ctk.CTkComboBox(filtros, values=TIPOS_RELATORIO, width=280, command=self._on_tipo_change)
        self.combo_tipo.grid(row=0, column=1, padx=8, pady=10, sticky="w")
        self.combo_tipo.set(TIPOS_RELATORIO[0])

        self.lbl_cliente = ctk.CTkLabel(filtros, text="Cliente:")
        self.lbl_cliente.grid(row=0, column=2, padx=(20, 8), pady=10, sticky="w")
        self.combo_cliente = ctk.CTkComboBox(filtros, values=[f"{c.id} - {c.nome}" for c in self.clientes], width=240)
        self.combo_cliente.grid(row=0, column=3, padx=8, pady=10, sticky="w")

        # Row 1: Mês / Ano (para Controle Mensal) & Datas (para Fluxo de Caixa)
        self.lbl_mes = ctk.CTkLabel(filtros, text="Mês/Ano:")
        self.lbl_mes.grid(row=1, column=0, padx=(20, 8), pady=(0, 10), sticky="w")
        
        frame_mes_ano = ctk.CTkFrame(filtros, fg_color="transparent")
        frame_mes_ano.grid(row=1, column=1, padx=8, pady=(0, 10), sticky="w")
        
        self.combo_mes = ctk.CTkComboBox(frame_mes_ano, values=MESES_NOME, width=140)
        self.combo_mes.pack(side="left", padx=(0, 5))
        hoje_mes_idx = date.today().month - 1
        self.combo_mes.set(MESES_NOME[hoje_mes_idx])

        anos_values = [str(a) for a in range(2024, 2031)]
        self.combo_ano = ctk.CTkComboBox(frame_mes_ano, values=anos_values, width=90)
        self.combo_ano.pack(side="left")
        self.combo_ano.set(str(date.today().year))

        # Datas Fluxo
        self.lbl_dt_inicio = ctk.CTkLabel(filtros, text="Início/Fim:")
        self.lbl_dt_inicio.grid(row=1, column=2, padx=(20, 8), pady=(0, 10), sticky="w")
        
        frame_datas = ctk.CTkFrame(filtros, fg_color="transparent")
        frame_datas.grid(row=1, column=3, padx=8, pady=(0, 10), sticky="w")
        self.entry_dt_inicio = ctk.CTkEntry(frame_datas, width=105, placeholder_text="dd/mm/aaaa")
        self.entry_dt_inicio.pack(side="left", padx=(0, 5))
        self.entry_dt_fim = ctk.CTkEntry(frame_datas, width=105, placeholder_text="dd/mm/aaaa")
        self.entry_dt_fim.pack(side="left")

        # Botão Gerar
        btn_gerar = ctk.CTkButton(filtros, text="📊 Gerar Relatório", fg_color="#00C853", hover_color="#00E676", command=self._on_gerar)
        btn_gerar.grid(row=1, column=4, padx=20, pady=(0, 10))

        # ── KPI Cards Frame (Para o Controle Mensal) ──
        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=20, pady=(0, 10))
        self._setup_kpi_cards()

        # ── Pré-visualização (Treeview) ──
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.tree = ttk.Treeview(table_frame, show="headings", style="Treeview")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self._on_tipo_change(TIPOS_RELATORIO[0])

        # ── Botões de Exportação ──
        export_frame = ctk.CTkFrame(self, fg_color="transparent")
        export_frame.pack(fill="x", padx=20, pady=(0, 20))

        btn_pdf = ctk.CTkButton(export_frame, text="📄 Exportar PDF", fg_color="#D32F2F", hover_color="#E53935", command=self._export_pdf)
        btn_pdf.pack(side="right", padx=8)

        btn_excel = ctk.CTkButton(export_frame, text="📗 Exportar Excel", fg_color="#2E7D32", hover_color="#43A047", command=self._export_excel)
        btn_excel.pack(side="right", padx=8)

    def _setup_kpi_cards(self):
        """Cria os 5 cards de resumo do Controle Mensal."""
        for child in self.kpi_frame.winfo_children():
            child.destroy()

        cards_def = [
            ("card_previsto", "📌 Previsto no Mês", "R$ 0,00", "#29B6F6"),
            ("card_realizado", "💰 Realizado no Mês", "R$ 0,00", "#00C853"),
            ("card_eficiencia", "📈 Eficiência Cobrança", "0.0%", "#AB47BC"),
            ("card_inadimplencia", "🚨 Inadimplência Mês", "R$ 0,00", "#FF5252"),
            ("card_lucro", "💡 Lucro Bruto Juros/Taxas", "R$ 0,00", "#FFA726"),
        ]

        self.kpi_labels = {}
        for idx, (key, title, default_val, color) in enumerate(cards_def):
            card = ctk.CTkFrame(self.kpi_frame, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=color)
            card.grid(row=0, column=idx, padx=4, pady=5, sticky="ew")
            self.kpi_frame.grid_columnconfigure(idx, weight=1)

            lbl_t = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11, weight="bold"), text_color="gray")
            lbl_t.pack(pady=(8, 2), padx=10)

            lbl_v = ctk.CTkLabel(card, text=default_val, font=ctk.CTkFont(size=15, weight="bold"), text_color=color)
            lbl_v.pack(pady=(0, 8), padx=10)
            self.kpi_labels[key] = lbl_v

    def _update_kpi_values(self, previsto: float, realizado: float, eficiencia: float, inadimplencia: float, lucro: float):
        fmt = lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.kpi_labels["card_previsto"].configure(text=fmt(previsto))
        self.kpi_labels["card_realizado"].configure(text=fmt(realizado))
        self.kpi_labels["card_eficiencia"].configure(text=f"{eficiencia:.1f}%")
        self.kpi_labels["card_inadimplencia"].configure(text=fmt(inadimplencia))
        self.kpi_labels["card_lucro"].configure(text=fmt(lucro))

    def _on_tipo_change(self, tipo):
        is_controle = tipo == "Controle Mensal (Previsto vs. Realizado)"
        is_extrato = tipo == "Extrato do Cliente"
        is_fluxo = tipo == "Fluxo de Caixa"

        # KPI Cards: exibe somente no Controle Mensal
        if is_controle:
            self.kpi_frame.pack(fill="x", padx=20, pady=(0, 10), before=self.tree.master)
        else:
            self.kpi_frame.pack_forget()

        # Controles
        self.combo_cliente.configure(state="normal" if is_extrato else "disabled")
        self.combo_mes.configure(state="normal" if is_controle else "disabled")
        self.combo_ano.configure(state="normal" if is_controle else "disabled")
        self.entry_dt_inicio.configure(state="normal" if is_fluxo else "disabled")
        self.entry_dt_fim.configure(state="normal" if is_fluxo else "disabled")

    def _on_gerar(self):
        tipo = self.combo_tipo.get()
        db = SessionLocal()
        try:
            if tipo == "Controle Mensal (Previsto vs. Realizado)":
                self._gerar_controle_mensal(db)
            elif tipo == "Extrato do Cliente":
                self._gerar_extrato(db)
            elif tipo == "Inadimplência":
                self._gerar_inadimplencia(db)
            elif tipo == "Fluxo de Caixa":
                self._gerar_fluxo(db)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar relatório:\n{str(e)}")
        finally:
            db.close()

    def _gerar_controle_mensal(self, db):
        mes_num = int(self.combo_mes.get().split(" - ")[0])
        ano_num = int(self.combo_ano.get())

        res = self.rel_service.controle_mensal(db, mes_num, ano_num)
        
        self._update_kpi_values(
            res["total_previsto"], res["total_realizado"],
            res["eficiencia_percentual"], res["total_inadimplencia"],
            res["total_lucro_juros"]
        )

        nome_mes = self.combo_mes.get().split(" - ")[1]
        self._titulo_atual = f"Controle Mensal — {nome_mes}/{ano_num}"
        self._subtitulo_atual = (
            f"Previsto: R$ {res['total_previsto']:,.2f} | Realizado: R$ {res['total_realizado']:,.2f} | "
            f"Eficiência: {res['eficiencia_percentual']}% | Inadimplência: R$ {res['total_inadimplencia']:,.2f}"
        ).replace(",", "X").replace(".", ",").replace("X", ".")

        self._colunas_atuais = [
            "Cliente", "Contrato", "Parcela", "Vencimento", 
            "Previsto (R$)", "Data Pagamento", "Realizado (R$)", "Tipo", "Status"
        ]
        self._dados_atuais = []

        fmt = lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        for r in res["rows"]:
            self._dados_atuais.append([
                r["cliente"], r["numero_contrato"], str(r["parcela_num"]),
                r["vencimento"], fmt(r["valor_previsto"]), r["data_pagamento"],
                fmt(r["valor_pago"]), r["tipo_pagamento"], r["status_rotulo"]
            ])

        self._render_tree()

    def _gerar_extrato(self, db):
        cliente_str = self.combo_cliente.get()
        if not cliente_str or " - " not in cliente_str:
            messagebox.showwarning("Aviso", "Selecione um cliente.")
            return

        cliente_id = int(cliente_str.split(" - ")[0])
        resultado = self.rel_service.extrato_cliente(db, cliente_id)

        if not resultado["cliente"]:
            messagebox.showinfo("Info", "Cliente não encontrado.")
            return

        cliente = resultado["cliente"]
        self._titulo_atual = "Extrato do Cliente"
        self._subtitulo_atual = f"{cliente.nome} — CPF: {cliente.cpf}"
        self._colunas_atuais = ["Contrato", "Parcela", "Vencimento", "Valor (R$)", "Status"]
        self._dados_atuais = []

        for grupo in resultado["emprestimos"]:
            emp = grupo["emprestimo"]
            for p in grupo["parcelas"]:
                venc = p.data_vencimento.strftime("%d/%m/%Y") if p.data_vencimento else "—"
                valor = f"R$ {p.valor_atualizado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                contrato = emp.numero_contrato or f"#{emp.id}"
                self._dados_atuais.append([
                    contrato, f"{p.numero}", venc, valor, p.status
                ])

        self._render_tree()

    def _gerar_inadimplencia(self, db):
        rows = self.rel_service.inadimplencia(db)
        self._titulo_atual = "Relatório de Inadimplência"
        self._subtitulo_atual = f"Gerado em {date.today().strftime('%d/%m/%Y')}"
        self._colunas_atuais = ["Cliente", "CPF", "Contrato", "Parcela", "Vencimento", "Valor (R$)", "Dias Atraso"]
        self._dados_atuais = []

        for r in rows:
            venc = r["vencimento"].strftime("%d/%m/%Y") if r["vencimento"] else "—"
            valor = f"R$ {r['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            self._dados_atuais.append([
                r["cliente"], r["cpf"], r["numero_contrato"],
                str(r["parcela_num"]), venc, valor, str(r["dias_atraso"])
            ])

        self._render_tree()

    def _gerar_fluxo(self, db):
        try:
            dt_ini = datetime.strptime(self.entry_dt_inicio.get(), "%d/%m/%Y").date()
            dt_fim = datetime.strptime(self.entry_dt_fim.get(), "%d/%m/%Y").date()
        except ValueError:
            messagebox.showwarning("Aviso", "Informe as datas no formato dd/mm/aaaa.")
            return

        rows = self.rel_service.fluxo_caixa(db, dt_ini, dt_fim)
        self._titulo_atual = "Fluxo de Caixa"
        self._subtitulo_atual = f"Período: {dt_ini.strftime('%d/%m/%Y')} a {dt_fim.strftime('%d/%m/%Y')}"
        self._colunas_atuais = ["Data", "Tipo", "Descrição", "Forma Pgto", "Valor (R$)", "Saldo Acum. (R$)"]
        self._dados_atuais = []

        for r in rows:
            dt = r["data"].strftime("%d/%m/%Y %H:%M") if r["data"] else "—"
            valor = f"R$ {r['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            saldo = f"R$ {r['saldo_acumulado']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            self._dados_atuais.append([
                dt, r["tipo"], r["descricao"], r["forma_pagamento"], valor, saldo
            ])

        self._render_tree()

    def _render_tree(self):
        # Limpar
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = self._colunas_atuais

        for col in self._colunas_atuais:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        for row in self._dados_atuais:
            self.tree.insert("", "end", values=row)

    def _check_data(self):
        if not self._dados_atuais:
            messagebox.showwarning("Aviso", "Gere um relatório primeiro antes de exportar.")
            return False
        return True

    def _export_pdf(self):
        if not self._check_data():
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            title="Salvar Relatório em PDF",
            initialfile=f"{self._titulo_atual.replace(' ', '_').replace('/', '_')}_{date.today().strftime('%Y%m%d')}.pdf"
        )
        if not filepath:
            return

        try:
            self.export_service.exportar_pdf(
                filepath, self._titulo_atual, self._colunas_atuais,
                self._dados_atuais, self._subtitulo_atual
            )
            messagebox.showinfo("Sucesso", f"PDF exportado com sucesso!\n{filepath}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar PDF:\n{str(e)}")

    def _export_excel(self):
        if not self._check_data():
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            title="Salvar Relatório em Excel",
            initialfile=f"{self._titulo_atual.replace(' ', '_').replace('/', '_')}_{date.today().strftime('%Y%m%d')}.xlsx"
        )
        if not filepath:
            return

        try:
            self.export_service.exportar_excel(
                filepath, self._titulo_atual, self._colunas_atuais,
                self._dados_atuais, self._subtitulo_atual
            )
            messagebox.showinfo("Sucesso", f"Excel exportado com sucesso!\n{filepath}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar Excel:\n{str(e)}")
