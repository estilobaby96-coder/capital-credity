import os
import sys
from datetime import date, timedelta
from database.connection import SessionLocal
from models.cliente import Cliente
from models.emprestimo import Emprestimo
from models.parcela import Parcela
from models.movimentacao import Movimentacao
from models.recebimento import Recebimento

from services.cliente_service import ClienteService
from services.emprestimo_service import EmprestimoService
from services.pagamento_service import PagamentoService
from services.relatorio_service import RelatorioService

def run_tests():
    print("Iniciando testes End-to-End no sistema...")
    
    db = SessionLocal()
    
    cli_service = ClienteService()
    emp_service = EmprestimoService()
    pag_service = PagamentoService()
    rel_service = RelatorioService()
    
    test_cpf = "999.999.999-99"
    test_cpf_clean = "99999999999"
    test_rg = "999999999"
    
    try:
        # 1. Limpar testes anteriores se existirem (fallback)
        print("Limpando dados residuais...")
        c_exist = db.query(Cliente).filter(Cliente.cpf == test_cpf_clean).first()
        if c_exist:
            db.delete(c_exist)
            db.commit()

        # 2. Testar Cadastro de Cliente
        print("Testando Cadastro de Cliente...")
        data = {
            "nome": "Cliente Teste E2E",
            "cpf": test_cpf,
            "rg": test_rg,
            "telefone": "(11) 99999-9999",
            "endereco": "Rua dos Testes, 123"
        }
        novo_cliente = cli_service.save_cliente(db=db, data=data)
        assert novo_cliente.id is not None, "Falha ao criar cliente."

        # 3. Testar Criação de Empréstimo
        print("Testando Criacao de Emprestimo (1000 reais, 10%, 5 parcelas)...")
        emp = emp_service.create_loan(
            db=db,
            cliente_id=novo_cliente.id,
            valor_solicitado=1000.0,
            taxa_juros=10.0,
            qtd_parcelas=5,
            data_inicio=date.today()
        )
        assert emp.id is not None, "Falha ao criar empréstimo."
        
        # Validar parcelas geradas
        parcelas = db.query(Parcela).filter(Parcela.emprestimo_id == emp.id).all()
        assert len(parcelas) == 5, "Falha: o sistema não gerou 5 parcelas."
        
        # 4. Testar Recebimento (Baixa de Parcela)
        print("Testando Pagamento de Parcela (Baixa)...")
        parcela_pagar = parcelas[0]
        pag_service.registrar_pagamento(
            db=db,
            parcela_id=parcela_pagar.id,
            valor_pago=float(parcela_pagar.valor_atualizado),
            metodo_pagamento="PIX"
        )
        
        # Validar status da parcela
        db.refresh(parcela_pagar)
        assert parcela_pagar.status == "PAGA", "Falha: a parcela não foi marcada como PAGA."
        
        # Validar caixa (Movimentação e Recebimento)
        mov = db.query(Movimentacao).filter(Movimentacao.descricao.like(f"%Parcela {parcela_pagar.numero}%")).first()
        assert mov is not None, "Falha: movimentação de caixa não foi gerada."
        assert mov.tipo == "ENTRADA", "Falha: a movimentação deveria ser ENTRADA."

        # 5. Testar Relatórios
        print("Testando Relatorios...")
        # Extrato
        extrato = rel_service.extrato_cliente(db, novo_cliente.id)
        assert extrato["cliente"] is not None
        assert len(extrato["emprestimos"]) > 0
        
        # Fluxo de Caixa
        fluxo = rel_service.fluxo_caixa(db, date.today() - timedelta(days=1), date.today() + timedelta(days=1))
        assert len(fluxo) > 0, "Falha: O fluxo de caixa não trouxe o pagamento feito no teste."

        print("=====================================")
        print("TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("=====================================")

    except AssertionError as ae:
        print(f"\nFALHA DE ASSERCAO: {ae}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # CLEANUP: Deletar todos os dados de teste
        print("Realizando faxina no banco de dados (apagando testes)...")
        try:
            c = db.query(Cliente).filter(Cliente.cpf == test_cpf_clean).first()
            if c:
                db.delete(c)
                db.commit()
                print("Lixo removido com sucesso.")
        except Exception as e:
            print(f"Erro ao limpar banco: {e}")
            db.rollback()
        db.close()

if __name__ == "__main__":
    run_tests()
