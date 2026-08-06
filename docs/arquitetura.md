# Arquitetura e Convenções (Fase 1)

O sistema **Capital Credity** foi concebido sob princípios rigorosos de Engenharia de Software.

## Princípios
- **Clean Architecture**: Regras de negócio isoladas (Services) do acesso a dados (Repositories/Models) e da interface (Views/Controllers).
- **SOLID & DRY**: Baixo acoplamento, alta coesão e não repetição de código.
- **MVC (Model-View-Controller)**: Fluxo de dados claro entre a interface do usuário (CustomTkinter) e o banco de dados (SQLite).

## Padrões de Código
- **Type Hints**: Obrigatórios para todas as funções e métodos.
- **Docstrings**: Formato padrão para todas as classes e funções públicas.
- **Tratamento de Exceções**: Completo, com logging de erros.
- **Dataclasses**: Utilizadas sempre que apropriado para transferência de dados.
- **PEP8**: Padrão oficial de codificação Python.

## Fluxo da Aplicação
1. `launcher.py` exibe a splash screen e inicializa configurações críticas.
2. `main.py` levanta o banco de dados, injeta dependências e abre a tela de Login.
3. Views acionam Controllers, que utilizam Services para lógica e Repositories para banco.
