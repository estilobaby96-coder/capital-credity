"""Dashboard — Tela inicial com cards de métricas financeiras e parcelas próximas."""

from datetime import date
import customtkinter as ctk
from tkinter import ttk
from database.connection import SessionLocal
from services.dashboard_service import DashboardService
from config.settings import (
    COLOR_PRIMARY, COLOR_SURFACE, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, COLOR_DANGER, FONT_SIZE_H1,
    FONT_SIZE_H2, FONT_SIZE_BODY, FONT_SIZE_SMALL
)


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.service = DashboardService()

        self._create_widgets()
        self._load_data()

    # ------------------------------------------------------------------ #
    #  Layout                                                              #
    # ------------------------------------------------------------------ #
    def _create_widgets(self):
        # ── Cabeçalho ──
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 4))

        lbl_titulo = ctk.CTkLabel(
            header, text="Dashboard Financeiro",
            font=ctk.CTkFont(size=FONT_SIZE_H1, weight="bold")
        )
        lbl_titulo.pack(side="left")

        self.lbl_data = ctk.CTkLabel(
            header, text=date.today().strftime("Hoje: %d/%m/%Y"),
            font=ctk.CTkFont(size=FONT_SIZE_BODY),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.lbl_data.pack(side="right")

        # ── Faixa de Cards (Linha 1) ──
        cards_row1 = ctk.CTkFrame(self, fg_color="transparent")
        cards_row1.pack(fill="x", padx=24, pady=(16, 4))
        cards_row1.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="cards")

        self.card_clientes     = self._make_card(cards_row1, "Clientes Cadastrados", "0", COLOR_PRIMARY, 0)
        self.card_ativos       = self._make_card(cards_row1, "Empréstimos Ativos",   "0", "#2196F3",     1)
        self.card_quitados     = self._make_card(cards_row1, "Empréstimos Quitados", "0", "#9E9E9E",     2)
        self.card_capital      = self._make_card(cards_row1, "Capital Emprestado",   "R$ 0,00", "#FF9800", 3)

        # ── Faixa de Cards (Linha 2) ──
        cards_row2 = ctk.CTkFrame(self, fg_color="transparent")
        cards_row2.pack(fill="x", padx=24, pady=(8, 4))
        cards_row2.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="cards2")

        self.card_a_vencer     = self._make_card(cards_row2, "Parcelas a Vencer",    "0", "#29B6F6",     0)
        self.card_atrasadas    = self._make_card(cards_row2, "Parcelas Atrasadas",   "0", COLOR_DANGER,  1)
        self.card_receber      = self._make_card(cards_row2, "Total a Receber",      "R$ 0,00", "#AB47BC", 2)
        self.card_recebido_mes = self._make_card(cards_row2, "Recebido no Mês",      "R$ 0,00", COLOR_PRIMARY, 3)

        # ── Recebido Hoje (Banner Destaque) ──
        banner = ctk.CTkFrame(self, fg_color="#1B5E20", corner_radius=12)
        banner.pack(fill="x", padx=24, pady=(16, 4))

        ctk.CTkLabel(
            banner, text="💰  Recebido Hoje",
            font=ctk.CTkFont(size=FONT_SIZE_H2, weight="bold"),
            text_color="#E8F5E9"
        ).pack(side="left", padx=20, pady=14)

        self.lbl_recebido_hoje = ctk.CTkLabel(
            banner, text="R$ 0,00",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#A5D6A7"
        )
        self.lbl_recebido_hoje.pack(side="right", padx=20, pady=14)

        # ── Tabela: Próximas Parcelas ──
        table_header = ctk.CTkFrame(self, fg_color="transparent")
        table_header.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(
            table_header, text="Próximas Parcelas a Vencer",
            font=ctk.CTkFont(size=FONT_SIZE_H2, weight="bold")
        ).pack(side="left")

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=24, pady=(4, 20))

        columns = ("cliente", "emprestimo", "parcela", "vencimento", "valor", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview", height=8)

        self.tree.heading("cliente",    text="Cliente")
        self.tree.heading("emprestimo", text="Contrato")
        self.tree.heading("parcela",    text="Parcela")
        self.tree.heading("vencimento", text="Vencimento")
        self.tree.heading("valor",      text="Valor")
        self.tree.heading("status",     text="Status")

        self.tree.column("cliente",    width=200, anchor="center")
        self.tree.column("emprestimo", width=100, anchor="center")
        self.tree.column("parcela",    width=80,  anchor="center")
        self.tree.column("vencimento", width=110, anchor="center")
        self.tree.column("valor",      width=120, anchor="center")
        self.tree.column("status",     width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ------------------------------------------------------------------ #
    #  Card factory                                                        #
    # ------------------------------------------------------------------ #
    def _make_card(self, parent, titulo: str, valor_inicial: str, accent_color: str, col: int):
        """Cria um card métrica e retorna a label de valor (para atualização)."""
        card = ctk.CTkFrame(parent, fg_color=COLOR_SURFACE, corner_radius=12)
        card.grid(row=0, column=col, padx=6, pady=6, sticky="nsew")

        # Faixa de cor (topo)
        accent = ctk.CTkFrame(card, fg_color=accent_color, height=4, corner_radius=0)
        accent.pack(fill="x")

        ctk.CTkLabel(
            card, text=titulo,
            font=ctk.CTkFont(size=FONT_SIZE_SMALL),
            text_color=COLOR_TEXT_SECONDARY
        ).pack(padx=14, pady=(10, 0), anchor="w")

        lbl_valor = ctk.CTkLabel(
            card, text=valor_inicial,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        lbl_valor.pack(padx=14, pady=(2, 14), anchor="w")

        return lbl_valor

    # ------------------------------------------------------------------ #
    #  Dados                                                               #
    # ------------------------------------------------------------------ #
    def _fmt(self, valor: float) -> str:
        """Formata um float para padrão monetário brasileiro."""
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _load_data(self):
        db = SessionLocal()
        try:
            m = self.service.get_metrics(db)

            # Atualizar Cards — Linha 1
            self.card_clientes.configure(text=str(m["total_clientes"]))
            self.card_ativos.configure(text=str(m["emprestimos_ativos"]))
            self.card_quitados.configure(text=str(m["emprestimos_quitados"]))
            self.card_capital.configure(text=self._fmt(m["capital_emprestado"]))

            # Atualizar Cards — Linha 2
            self.card_a_vencer.configure(text=str(m["parcelas_a_vencer"]))
            self.card_atrasadas.configure(text=str(m["parcelas_atrasadas"]))
            self.card_receber.configure(text=self._fmt(m["valor_a_receber"]))
            self.card_recebido_mes.configure(text=self._fmt(m["valor_recebido_mes"]))

            # Banner Destaque
            self.lbl_recebido_hoje.configure(text=self._fmt(m["valor_recebido_hoje"]))

            # Tabela de Próximas Parcelas
            for item in self.tree.get_children():
                self.tree.delete(item)

            parcelas = self.service.get_proximas_parcelas(db, limite=10)
            for p in parcelas:
                nome_cliente = p.emprestimo.cliente.nome if p.emprestimo and p.emprestimo.cliente else "—"
                emp_contrato = p.emprestimo.numero_contrato if p.emprestimo and p.emprestimo.numero_contrato else f"#{p.emprestimo_id}"
                num_parcela = f"{p.numero}"
                venc = p.data_vencimento.strftime("%d/%m/%Y") if p.data_vencimento else "—"
                valor = self._fmt(p.valor_atualizado)
                status = p.status

                self.tree.insert("", "end", values=(
                    nome_cliente, emp_contrato, num_parcela, venc, valor, status
                ))
        finally:
            db.close()
