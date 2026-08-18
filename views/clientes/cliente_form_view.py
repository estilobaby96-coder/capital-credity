"""Tela de Formulário (Modal) para cadastro e edição de clientes."""

import customtkinter as ctk
import base64
import os
from tkinter import messagebox, filedialog
from database.connection import SessionLocal
from services.cliente_service import ClienteService, ValidationError

class ClienteFormView(ctk.CTkToplevel):
    def __init__(self, master, on_save_callback, cliente=None):
        super().__init__(master)
        
        self.on_save_callback = on_save_callback
        self.cliente = cliente
        self.service = ClienteService()
        self.doc_identidade_b64 = ""
        self.doc_endereco_b64 = ""
        
        titulo = "Editar Cliente" if cliente else "Novo Cliente"
        self.title(titulo)
        self.geometry("500x750")
        self.minsize(450, 600)
        
        # Centralizar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (750 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.grab_set()  # Modal
        
        self._create_widgets()
        if self.cliente:
            self._load_data()

    def _create_widgets(self):
        # Título
        lbl_titulo = ctk.CTkLabel(self, text="Dados do Cliente", font=ctk.CTkFont(size=20, weight="bold"))
        lbl_titulo.pack(pady=(20, 10))
        
        # Frame com scroll
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Campos
        self.entry_nome = self._create_field("Nome Completo *", self.scroll_frame)
        self.entry_cpf = self._create_field("CPF * (Apenas números)", self.scroll_frame)
        self.entry_telefone = self._create_field("Telefone", self.scroll_frame)
        self.entry_email = self._create_field("E-mail", self.scroll_frame)
        self.entry_cep = self._create_field("CEP (Apenas números)", self.scroll_frame)
        self.entry_endereco = self._create_field("Endereço (Rua, Bairro)", self.scroll_frame)
        self.entry_cidade = self._create_field("Cidade / UF", self.scroll_frame)
        
        # ── Seção de Documentos ──────────────────────────────────
        lbl_docs = ctk.CTkLabel(self.scroll_frame, text="📄 Documentos", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_docs.pack(padx=20, pady=(20, 5), anchor="w")
        
        separator = ctk.CTkFrame(self.scroll_frame, height=2, fg_color="#565b5e")
        separator.pack(fill="x", padx=20, pady=(0, 10))

        # Doc Identidade
        frame_id = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_id.pack(fill="x", padx=20, pady=(5, 0))
        
        lbl_id = ctk.CTkLabel(frame_id, text="RG / CPF (Foto/Digitalização):", anchor="w")
        lbl_id.pack(side="left")
        
        self.lbl_id_status = ctk.CTkLabel(frame_id, text="Nenhum arquivo", text_color="gray", anchor="e")
        self.lbl_id_status.pack(side="right")
        
        btn_id = ctk.CTkButton(self.scroll_frame, text="📎 Selecionar Arquivo de Identidade", 
                               fg_color="#29B6F6", hover_color="#0288D1",
                               command=lambda: self._select_file("identidade"))
        btn_id.pack(padx=20, pady=(5, 5), fill="x")
        
        # Doc Endereço
        frame_end = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_end.pack(fill="x", padx=20, pady=(10, 0))
        
        lbl_end = ctk.CTkLabel(frame_end, text="Comprovante de Endereço:", anchor="w")
        lbl_end.pack(side="left")
        
        self.lbl_end_status = ctk.CTkLabel(frame_end, text="Nenhum arquivo", text_color="gray", anchor="e")
        self.lbl_end_status.pack(side="right")
        
        btn_end = ctk.CTkButton(self.scroll_frame, text="📎 Selecionar Comprovante de Endereço", 
                                fg_color="#29B6F6", hover_color="#0288D1",
                                command=lambda: self._select_file("endereco"))
        btn_end.pack(padx=20, pady=(5, 5), fill="x")
        
        # Binds para máscaras
        self.entry_cpf.bind("<KeyRelease>", self._format_cpf)
        self.entry_telefone.bind("<KeyRelease>", self._format_telefone)
        self.entry_cep.bind("<KeyRelease>", self._format_cep)
        
        # Botões
        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.pack(pady=30, fill="x", padx=40)
        
        btn_cancelar = ctk.CTkButton(frame_botoes, text="Cancelar", fg_color="gray", command=self.destroy)
        btn_cancelar.pack(side="left", expand=True, padx=5)
        
        btn_salvar = ctk.CTkButton(frame_botoes, text="Salvar", command=self._save)
        btn_salvar.pack(side="right", expand=True, padx=5)

    def _select_file(self, tipo):
        """Abre um diálogo para selecionar arquivo de imagem ou PDF."""
        filepath = filedialog.askopenfilename(
            parent=self,
            title=f"Selecionar {'Identidade' if tipo == 'identidade' else 'Comprovante de Endereço'}",
            filetypes=[
                ("Imagens e PDFs", "*.png *.jpg *.jpeg *.bmp *.gif *.pdf"),
                ("Imagens", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("PDF", "*.pdf"),
                ("Todos os Arquivos", "*.*")
            ]
        )
        if filepath:
            try:
                with open(filepath, "rb") as f:
                    file_bytes = f.read()
                
                # Determinar o MIME type
                ext = os.path.splitext(filepath)[1].lower()
                mime_map = {
                    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                    ".bmp": "image/bmp", ".gif": "image/gif", ".pdf": "application/pdf"
                }
                mime = mime_map.get(ext, "application/octet-stream")
                
                b64_string = f"data:{mime};base64,{base64.b64encode(file_bytes).decode('utf-8')}"
                filename = os.path.basename(filepath)
                
                if tipo == "identidade":
                    self.doc_identidade_b64 = b64_string
                    self.lbl_id_status.configure(text=f"✅ {filename}", text_color="#00C853")
                else:
                    self.doc_endereco_b64 = b64_string
                    self.lbl_end_status.configure(text=f"✅ {filename}", text_color="#00C853")
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler o arquivo:\n{str(e)}")

    def _create_field(self, label_text, parent=None):
        if parent is None:
            parent = self
        lbl = ctk.CTkLabel(parent, text=label_text, anchor="w")
        lbl.pack(padx=20, pady=(10, 0), fill="x")
        entry = ctk.CTkEntry(parent)
        entry.pack(padx=20, pady=(2, 0), fill="x")
        return entry

    def _format_cpf(self, event):
        # Ignorar backspace ou delete para não bugar a deleção
        if event.keysym in ('BackSpace', 'Delete'):
            return
            
        text = self.entry_cpf.get()
        digits = ''.join(filter(str.isdigit, text))
        
        if len(digits) > 11:
            digits = digits[:11]
            
        formatted = ""
        if len(digits) > 0:
            if len(digits) <= 3:
                formatted = digits
            elif len(digits) <= 6:
                formatted = f"{digits[:3]}.{digits[3:]}"
            elif len(digits) <= 9:
                formatted = f"{digits[:3]}.{digits[3:6]}.{digits[6:]}"
            else:
                formatted = f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"
                
        self.entry_cpf.delete(0, 'end')
        self.entry_cpf.insert(0, formatted)
        
    def _format_telefone(self, event):
        if event.keysym in ('BackSpace', 'Delete'):
            return
            
        text = self.entry_telefone.get()
        digits = ''.join(filter(str.isdigit, text))
        
        if len(digits) > 11:
            digits = digits[:11]
            
        formatted = ""
        if len(digits) > 0:
            if len(digits) <= 2:
                formatted = f"({digits}"
            elif len(digits) <= 6:
                formatted = f"({digits[:2]}) {digits[2:]}"
            elif len(digits) <= 10:
                formatted = f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
            else:
                formatted = f"({digits[:2]}) {digits[2:7]}-{digits[7:11]}"
                
        self.entry_telefone.delete(0, 'end')
        self.entry_telefone.insert(0, formatted)

    def _format_cep(self, event):
        if event.keysym in ('BackSpace', 'Delete'):
            return
            
        text = self.entry_cep.get()
        digits = ''.join(filter(str.isdigit, text))
        
        if len(digits) > 8:
            digits = digits[:8]
            
        formatted = ""
        if len(digits) > 0:
            if len(digits) <= 5:
                formatted = digits
            else:
                formatted = f"{digits[:5]}-{digits[5:8]}"
                
        self.entry_cep.delete(0, 'end')
        self.entry_cep.insert(0, formatted)
        
        if len(digits) == 8:
            import threading
            threading.Thread(target=self._buscar_cep, args=(digits,), daemon=True).start()

    def _buscar_cep(self, cep):
        import requests
        try:
            resp = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if not data.get("erro"):
                    log = data.get("logradouro", "")
                    bairro = data.get("bairro", "")
                    endereco_completo = f"{log}, {bairro}".strip(", ")
                    cidade_uf = f"{data.get('localidade', '')} / {data.get('uf', '')}"
                    self.after(0, self._fill_address, endereco_completo, cidade_uf)
        except Exception:
            pass

    def _fill_address(self, endereco, cidade):
        self.entry_endereco.delete(0, 'end')
        self.entry_endereco.insert(0, endereco)
        self.entry_cidade.delete(0, 'end')
        self.entry_cidade.insert(0, cidade)

    def _load_data(self):
        self.entry_nome.insert(0, self.cliente.nome)
        if self.cliente.cpf:
            self.entry_cpf.insert(0, self.cliente.cpf)
        if self.cliente.telefone:
            self.entry_telefone.insert(0, self.cliente.telefone)
        if self.cliente.email:
            self.entry_email.insert(0, self.cliente.email)
        if self.cliente.cep:
            self.entry_cep.insert(0, self.cliente.cep)
        if self.cliente.endereco:
            self.entry_endereco.insert(0, self.cliente.endereco)
        if self.cliente.cidade:
            self.entry_cidade.insert(0, self.cliente.cidade)
        
        # Carregar estado dos documentos existentes
        if self.cliente.doc_identidade:
            self.doc_identidade_b64 = self.cliente.doc_identidade
            self.lbl_id_status.configure(text="✅ Documento cadastrado", text_color="#00C853")
        if self.cliente.doc_endereco:
            self.doc_endereco_b64 = self.cliente.doc_endereco
            self.lbl_end_status.configure(text="✅ Documento cadastrado", text_color="#00C853")

    def _save(self):
        data = {
            "nome": self.entry_nome.get().strip(),
            "cpf": self.entry_cpf.get().strip(),
            "telefone": self.entry_telefone.get().strip(),
            "email": self.entry_email.get().strip(),
            "cep": self.entry_cep.get().strip(),
            "endereco": self.entry_endereco.get().strip(),
            "cidade": self.entry_cidade.get().strip(),
            "doc_identidade": self.doc_identidade_b64,
            "doc_endereco": self.doc_endereco_b64
        }
        
        db = SessionLocal()
        try:
            cliente_id = self.cliente.id if self.cliente else None
            self.service.save_cliente(db, data, cliente_id)
            messagebox.showinfo("Sucesso", "Cliente salvo com sucesso!")
            self.on_save_callback()
            self.destroy()
        except ValidationError as e:
            messagebox.showwarning("Aviso", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar:\n{str(e)}")
        finally:
            db.close()

