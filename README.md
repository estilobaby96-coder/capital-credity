# Capital Credity - Gestor Financeiro de Empréstimos

Software comercial de nível profissional para gerenciamento de empréstimos particulares.

## Funcionalidades
- Cadastro de clientes e empréstimos
- Controle financeiro, parcelas e juros
- Recebimentos e renegociações
- Relatórios, contratos e recibos
- Dashboard corporativo
- Segurança, backup e auditoria

## Tecnologias
- Python 3.13+
- CustomTkinter
- SQLite / SQLAlchemy / Alembic
- Pillow, ReportLab, OpenPyXL, Matplotlib
- bcrypt, PyInstaller

## Instalação e Execução (Desenvolvimento)
1. Crie um ambiente virtual: `python -m venv venv`
2. Ative o ambiente virtual.
3. Instale as dependências: `pip install -r requirements.txt`
4. Execute o sistema: `python launcher.py`

## Documentação e Arquitetura
Consulte os arquivos na pasta `docs/` para entender as convenções e a estrutura do projeto:
- `docs/arquitetura.md` — Arquitetura técnica e estrutural do projeto.
- `docs/regras_de_negocio.md` — Bíblia Operacional: regras de crédito, limites, modalidades de parcelamento (Mensal, Semanal, Quinzenal), multas e lógicas financeiras.
