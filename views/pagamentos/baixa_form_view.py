"""Tela de Formulário (Modal) para realizar a baixa de uma parcela."""

from datetime import date
from dateutil.relativedelta import relativedelta
import customtkinter as ctk
from tkinter import messagebox
from database.connection import SessionLocal
from services.pagamento_service import PagamentoService

class BaixaFormView(ctk.CTkToplevel):
    def __init__(self, master, parcela, on_save_callback):
        super().__init__(master)
        
        self.on_save_callback = on_save_callback
        self.parcela = parcela
        self.service = PagamentoService()
        
        self.title("Receber Pagamento (Baixa)")
        self.geometry("520x640")
        self.minsize(450, 500)
        self.resizable(True, True)
        
        # Centralizar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (520 // 2)
        y = (self.winfo_screenheight() // 2) - (640 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.grab_set()
        
        self._create_widgets()
        self._load_data()

    def _fmt(self, valor: float) -> str:
        """Formata float para padrão monetário brasileiro."""
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _create_widgets(self):
        lbl_titulo = ctk.CTkLabel(self, text="Detalhes do Recebimento", font=ctk.CTkFont(size=20, weight="bold"))
        lbl_titulo.pack(pady=(20, 10))
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Infos da Parcela (Apenas Leitura)
        self.lbl_info = ctk.CTkLabel(self.scroll_frame, text="", text_color="gray", justify="center")
        self.lbl_info.pack(pady=(0, 5))

        # Indicador de tipo de pagamento
        self.lbl_tipo = ctk.CTkLabel(self.scroll_frame, text="", font=ctk.CTkFont(size=13, weight="bold"),
                                     text_color="#FF9800", wraplength=440, justify="center")
        self.lbl_tipo.pack(pady=(0, 15))
        
        # Valor Pago
        ctk.CTkLabel(self.scroll_frame, text="Valor Recebido (R$) *", anchor="w").pack(padx=20, pady=(5, 0), fill="x")
        self.entry_valor = ctk.CTkEntry(self.scroll_frame)
        self.entry_valor.pack(padx=20, pady=(2, 0), fill="x")
        self.entry_valor.bind("<KeyRelease>", self._on_valor_changed)
        
        # Taxa de Serviço / Rolagem (Opcional)
        ctk.CTkLabel(self.scroll_frame, text="Taxa de Serviço / Rolagem (R$) (Opcional)", anchor="w", text_color="#29B6F6").pack(padx=20, pady=(10, 0), fill="x")
        self.entry_taxa = ctk.CTkEntry(self.scroll_frame, placeholder_text="0.00")
        self.entry_taxa.pack(padx=20, pady=(2, 0), fill="x")

        # Forma de Pagamento
        ctk.CTkLabel(self.scroll_frame, text="Forma de Pagamento *", anchor="w").pack(padx=20, pady=(10, 0), fill="x")
        metodos = ["PIX", "Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Transferência Bancária", "Boleto"]
        self.combo_metodo = ctk.CTkComboBox(self.scroll_frame, values=metodos)
        self.combo_metodo.pack(padx=20, pady=(2, 0), fill="x")
        self.combo_metodo.set("PIX")
        
        # Observação
        ctk.CTkLabel(self.scroll_frame, text="Observação (Opcional)", anchor="w").pack(padx=20, pady=(10, 0), fill="x")
        self.entry_obs = ctk.CTkEntry(self.scroll_frame)
        self.entry_obs.pack(padx=20, pady=(2, 0), fill="x")
        
        # Botões
        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.pack(pady=25, fill="x", padx=40)
        
        btn_cancelar = ctk.CTkButton(frame_botoes, text="Cancelar", fg_color="gray", command=self.destroy)
        btn_cancelar.pack(side="left", expand=True, padx=5)
        
        self.btn_salvar = ctk.CTkButton(frame_botoes, text="Confirmar Recebimento", fg_color="#00C853", hover_color="#00E676", command=self._save)
        self.btn_salvar.pack(side="right", expand=True, padx=5)

    def _load_data(self):
        vencimento_str = self.parcela.data_vencimento.strftime("%d/%m/%Y")
        capital_fmt = self._fmt(self.parcela.capital)
        juros_fmt = self._fmt(self.parcela.juros)
        total_fmt = self._fmt(self.parcela.valor_atualizado)
        
        info = (f"Empréstimo #{self.parcela.emprestimo_id}\n"
                f"Vencimento: {vencimento_str}\n"
                f"Capital: {capital_fmt}  |  Juros: {juros_fmt}\n"
                f"Valor Total do Empréstimo: {total_fmt}")
        self.lbl_info.configure(text=info)
        
        # Pré-preencher o valor total
        self.entry_valor.insert(0, f"{self.parcela.valor_atualizado:.2f}")
        self._update_tipo_label(self.parcela.valor_atualizado)

    def _on_valor_changed(self, event=None):
        """Atualiza o indicador de tipo conforme o usuário digita."""
        try:
            valor = float(self.entry_valor.get().replace(",", "."))
            self._update_tipo_label(valor)
        except ValueError:
            self.lbl_tipo.configure(text="", text_color="#FF9800")

    def _update_tipo_label(self, valor: float):
        """Mostra ao operador que tipo de pagamento será registrado."""
        tolerancia = 0.01
        total = self.parcela.valor_atualizado
        juros = self.parcela.juros

        if valor <= 0:
            self.lbl_tipo.configure(text="⚠ Valor inválido", text_color="#FF5252")
        elif abs(valor - total) <= tolerancia or valor >= total:
            self.lbl_tipo.configure(
                text="✅ Pagamento INTEGRAL — Empréstimo será QUITADO",
                text_color="#00C853"
            )
        elif abs(valor - juros) <= tolerancia:
            nova_data = self.parcela.data_vencimento + relativedelta(months=1)
            self.lbl_tipo.configure(
                text=(f"🔄 ROLAGEM — Só juros pagos\n"
                      f"O empréstimo será renovado para {nova_data.strftime('%d/%m/%Y')} "
                      f"com valor cheio de {self._fmt(self.parcela.capital + self.parcela.juros)}."),
                text_color="#FF9800"
            )
        else:
            self.lbl_tipo.configure(
                text=f"❌ BLOQUEADO — Sem abatimentos. Pague os JUROS ou o TOTAL.",
                text_color="#FF5252"
            )

    def _save(self):
        try:
            valor_pago = float(self.entry_valor.get().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Aviso", "O valor informado é inválido.")
            return

        taxa_servico = 0.0
        taxa_str = self.entry_taxa.get().strip()
        if taxa_str:
            try:
                taxa_servico = float(taxa_str.replace(",", "."))
            except ValueError:
                messagebox.showwarning("Aviso", "A taxa de serviço informada é inválida.")
                return

        if valor_pago <= 0:
            messagebox.showwarning("Aviso", "O valor deve ser maior que zero.")
            return

        metodo = self.combo_metodo.get()
        obs = self.entry_obs.get().strip()
        
        tolerancia = 0.01
        
        # Confirmação para rolagem (só juros)
        if abs(valor_pago - self.parcela.juros) <= tolerancia:
            nova_data = self.parcela.data_vencimento + relativedelta(months=1)
            msg_t = f" + R$ {taxa_servico:.2f} (Taxa Servico)" if taxa_servico > 0 else ""
            resp = messagebox.askyesno(
                "Confirmar Rolagem",
                f"O cliente pagará os juros ({self._fmt(self.parcela.juros)}){msg_t}.\n\n"
                f"O empréstimo será renovado para {nova_data.strftime('%d/%m/%Y')} "
                f"com o valor cheio de {self._fmt(self.parcela.capital + self.parcela.juros)}.\n\n"
                f"Confirmar a rolagem?"
            )
            if not resp:
                return
        
        # Bloqueio para pagamento parcial
        elif valor_pago < (self.parcela.valor_atualizado - tolerancia):
            messagebox.showwarning(
                "Operação Bloqueada",
                f"O sistema não permite abatimentos parciais.\n\n"
                f"O valor recebido ({self._fmt(valor_pago)}) é diferente de juros e do total.\n"
                f"Você deve cobrar o JUROS ({self._fmt(self.parcela.juros)}) ou o TOTAL ({self._fmt(self.parcela.valor_atualizado)})."
            )
            return

        db = SessionLocal()
        try:
            resultado = self.service.registrar_pagamento(db, self.parcela.id, valor_pago, metodo, obs, taxa_servico)
            messagebox.showinfo("Sucesso", resultado["mensagem"])
            self.on_save_callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao processar a baixa:\n{str(e)}")
        finally:
            db.close()
